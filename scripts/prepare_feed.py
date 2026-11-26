#!/usr/bin/env python3
"""Prepare the cached arXiv feed as data and content for Nida."""

import json
import re
import tempfile
import tomllib
from datetime import date, datetime, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from fastembed import TextEmbedding
from huggingface_hub import hf_hub_download


VERSION_SUFFIX = re.compile(r"v\d+$")
MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_REPOSITORY = "qdrant/bge-small-en-v1.5-onnx-q"
MODEL_REVISION = "aa8f8b060edb00e03bfdd08813a2949946c8ba55"
MODEL_FILES = [
    "config.json", "model_optimized.onnx", "special_tokens_map.json",
    "tokenizer.json", "tokenizer_config.json",
]


def compile_terms(terms: list[str]) -> re.Pattern:
    """Match complete terms, allowing spaces and hyphens within phrases."""
    separator = r"[\s\u2010-\u2015-]+"
    phrases = [
        separator.join(map(re.escape, re.split(separator, term.strip())))
        for term in terms
        if term.strip()
    ]
    pattern = r"\b(?:" + "|".join(phrases) + r")\b" if phrases else r"(?!)"
    return re.compile(pattern, re.IGNORECASE)


class SemanticFocus:
    def __init__(self, config: dict, cache_dir: Path):
        self.profiles = {
            code: section for code, section in config.get("focus", {}).items()
            if section.get("descriptions")
        }
        semantic = config.get("semantic", {})
        self.background = semantic.get("background", [])
        self.min_margin = semantic.get("min_margin", 0.015)
        self.cache_dir = cache_dir
        self.model = None
        self.profile_vectors = {}
        self.background_vectors = None
        self.used_vectors = set()

    def _embed(self, documents: list[str]) -> np.ndarray:
        if self.model is None:
            model_files = [
                Path(hf_hub_download(
                    repo_id=MODEL_REPOSITORY, revision=MODEL_REVISION, filename=filename,
                    cache_dir=self.cache_dir, token=False,
                ))
                for filename in MODEL_FILES
            ]
            self.model = TextEmbedding(
                model_name=MODEL_NAME, threads=4,
                cache_dir=str(self.cache_dir), specific_model_path=str(model_files[0].parent),
            )
        ordering = sorted(range(len(documents)), key=lambda index: len(documents[index]))
        batches = self.model.embed([documents[index] for index in ordering], batch_size=16)
        return np.stack(list(batches))[np.argsort(ordering)]

    def _paper_vectors(self, documents: list[str]) -> np.ndarray:
        signature = json.dumps([MODEL_REVISION, documents], ensure_ascii=False)
        digest = sha256(signature.encode("utf-8")).hexdigest()
        path = self.cache_dir / f"embeddings-v1-{digest}.npy"
        self.used_vectors.add(path)
        try:
            return np.load(path, allow_pickle=False)
        except (OSError, ValueError, EOFError):
            pass

        print(f"Computing embeddings for {len(documents)} papers.", flush=True)
        vectors = self._embed(documents)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with BytesIO() as buffer:
            np.save(buffer, vectors, allow_pickle=False)
            write_if_changed(path, buffer.getvalue())
        return vectors

    def classify(self, papers: list[dict]) -> list[tuple[str, float] | None]:
        """Score each title and abstract against the same topic descriptions."""
        if not papers or not self.profiles:
            return [None] * len(papers)

        documents = [f"{paper['title']}\n{paper['summary']}" for paper in papers]
        try:
            if not self.profile_vectors:
                profile_vectors = {
                    code: self._embed(section["descriptions"])
                    for code, section in self.profiles.items()
                }
                self.background_vectors = self._embed(self.background) if self.background else None
                self.profile_vectors = profile_vectors
            vectors = self._paper_vectors(documents)
        except Exception as error:
            raise RuntimeError("Could not score papers with the semantic focus model") from error

        general = 0 if self.background_vectors is None else (vectors @ self.background_vectors.T).max(axis=1)
        codes = list(self.profile_vectors)
        scores = np.column_stack([
            (vectors @ self.profile_vectors[code].T).max(axis=1)
            for code in codes
        ])
        best = scores.argmax(axis=1)
        margins = scores[np.arange(len(papers)), best] - general
        return [
            (codes[index], float(margin)) if margin > self.min_margin else None
            for index, margin in zip(best, margins, strict=True)
        ]


class Feed:
    def __init__(self, config: dict, cache_dir: Path = Path(".nida/models")):
        self.categories = config["categories"]
        self.focus = config.get("focus", {})
        self.semantic = SemanticFocus(config, cache_dir)
        self.highlights = compile_terms(config.get("highlights", {}).get("words", []))
        self.max_authors = config["settings"]["max_authors_display"]

    def group_papers(self, stored_categories: dict) -> dict:
        sections = {code: [] for code in [*self.focus, *self.categories]}
        papers_by_id = {}
        for code in self.categories:
            for paper in stored_categories.get(code, {}).get("papers", []):
                paper_id = VERSION_SUFFIX.sub("", paper["id"])
                primary = paper.get("primary_category") or next(iter(paper.get("categories", [])), None)
                if paper_id not in papers_by_id or code == primary:
                    papers_by_id[paper_id] = (paper, code)

        ordered_papers = sorted(
            papers_by_id.values(), key=lambda item: item[0]["submitted_date"], reverse=True
        )
        semantic_matches = self.semantic.classify([paper for paper, _ in ordered_papers])
        focus_ranks = {}
        for (paper, code), match in zip(ordered_papers, semantic_matches, strict=True):
            if match:
                code, margin = match
                focus_ranks[paper["id"]] = margin
            sections[code].append(paper)

        for code in self.focus:
            sections[code].sort(key=lambda paper: focus_ranks.get(paper["id"], 0), reverse=True)
        return {code: papers for code, papers in sections.items() if papers}

    def format_paper(self, paper: dict) -> dict:
        title = paper["title"]
        title_parts = []
        end = 0
        for match in self.highlights.finditer(title):
            if match.start() > end:
                title_parts.append({"text": title[end:match.start()]})
            title_parts.append({"text": match.group(), "highlight": True})
            end = match.end()
        if title[end:]:
            title_parts.append({"text": title[end:]})

        authors = paper.get("authors") or paper.get("display_authors", [])
        display_authors = authors[:self.max_authors]
        if len(authors) > self.max_authors:
            display_authors.append("et al.")

        arxiv_id = paper["id"]
        return {
            "id": arxiv_id,
            "title_parts": title_parts,
            "authors": ", ".join(display_authors),
            "summary": paper["summary"],
            "comments": paper.get("comments") or "",
            "arxiv_url": paper["arxiv_url"],
            "pdf_url": paper["pdf_url"],
            "doi": f"https://doi.org/10.48550/arXiv.{VERSION_SUFFIX.sub('', arxiv_id)}",
            "submitted": datetime.fromisoformat(paper["submitted_date"]).date().isoformat(),
        }

    def issue(self, daily_data: dict) -> dict | None:
        day = date.fromisoformat(daily_data["date"]).isoformat()
        updated = datetime.fromisoformat(daily_data["generated_at"])
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        groups = self.group_papers(daily_data["categories"])
        if not groups:
            return None

        expanded = self.focus.keys() & groups.keys() or {next(iter(groups))}
        sections = []
        for code, papers in groups.items():
            name = self.focus[code]["name"] if code in self.focus else self.categories[code]
            sections.append({
                "class": re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-"),
                "name": name,
                "expanded": code in expanded,
                "papers": [self.format_paper(paper) for paper in papers],
            })
        return {
            "date": day,
            "count": sum(map(len, groups.values())),
            "updated": updated.astimezone(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M %Z"),
            "sections": sections,
        }


def write_if_changed(path: Path, content: str | bytes) -> None:
    if isinstance(content, str):
        content = content.encode("utf-8")
    if path.is_file() and path.read_bytes() == content:
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(content)
            file.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def prepare_feed(root: Path) -> None:
    with (root / "config.toml").open("rb") as file:
        config = tomllib.load(file)
    feed = Feed(config["extra"]["feed"], root / ".nida/models")
    issues = {}
    for path in sorted((root / "data").glob("*.json"), reverse=True):
        try:
            issue = feed.issue(json.loads(path.read_text(encoding="utf-8")))
            if issue:
                issues.setdefault(issue["date"], issue)
        except (OSError, AttributeError, KeyError, TypeError, ValueError) as error:
            print(f"Skipping {path.name}: {error}")

    content_dir = root / config["content_dir"]
    data_dir = root / config["data_dir"]
    content_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    write_if_changed(content_dir / "_index.md", '+++\ntemplate = "index"\n+++\n')
    dates = sorted(issues, reverse=True)
    page_paths = set()
    for day in dates:
        path = content_dir / f"issue-{day}.md"
        page_paths.add(path)
        write_if_changed(path, f'+++\ntitle = "{day}"\ndate = {day}\npath = "/days/{day}/"\n+++\n')
    write_if_changed(
        data_dir / "feed.json",
        json.dumps({"dates": dates, "issues": issues}, ensure_ascii=False, separators=(",", ":")) + "\n",
    )
    for stale_path in set(content_dir.glob("issue-*.md")) - page_paths:
        stale_path.unlink(missing_ok=True)
    for unused_path in set(feed.semantic.cache_dir.glob("embeddings-v1-*.npy")) - feed.semantic.used_vectors:
        unused_path.unlink(missing_ok=True)

    print(f"Prepared {len(dates)} day(s) for Nida.")


if __name__ == "__main__":
    prepare_feed(Path(__file__).resolve().parents[1])
