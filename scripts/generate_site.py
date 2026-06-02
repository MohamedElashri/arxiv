#!/usr/bin/env python3
"""
Static site generator for ArXiv daily papers.
Generates HTML pages from JSON data files.
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re
from zoneinfo import ZoneInfo

try:
    import tomllib
    _USES_STDLIB_TOML = True
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import toml as tomllib
    _USES_STDLIB_TOML = False


class SiteGenerator:
    def __init__(self, config_path: str = "config.toml"):
        """Initialize the site generator with configuration."""
        mode = "rb" if _USES_STDLIB_TOML else "r"
        with open(config_path, mode) as f:
            self.config = tomllib.load(f)
        self.data_dir = Path("data")
        self.templates_dir = Path("templates")
        self.output_dir = Path("site")  # Generated static site files
        self.output_dir.mkdir(exist_ok=True)
        
        # Create assets directories
        (self.output_dir / "css").mkdir(exist_ok=True)
        (self.output_dir / "js").mkdir(exist_ok=True)
    
    def get_valid_data_files(self) -> List[Path]:
        """Get all valid JSON data files, sorted by date (newest first)."""
        data_files = []
        
        # Find all JSON files in data directory
        for json_file in self.data_dir.glob("*.json"):
            try:
                # Try to load and validate the JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it has the required structure
                if self.validate_json_structure(data):
                    data_files.append(json_file)
                else:
                    print(f"Warning: {json_file} has invalid structure, skipping")
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not read {json_file}: {e}")
                continue
        
        # Sort by filename (which should be date format YYYY-MM-DD)
        return sorted(data_files, reverse=True)
    
    def validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that JSON data has the required structure for site generation."""
        required_keys = ["date", "generated_at", "categories"]
        
        # Check for required top-level keys
        for key in required_keys:
            if key not in data:
                return False
        
        # Validate date format
        try:
            datetime.fromisoformat(data["date"])
            datetime.fromisoformat(data["generated_at"])
        except (ValueError, TypeError):
            return False
        
        # Validate categories structure
        if not isinstance(data["categories"], dict):
            return False
        
        # Check each category has required structure
        for category_code, category_data in data["categories"].items():
            if not isinstance(category_data, dict):
                return False
            if "name" not in category_data or "papers" not in category_data:
                return False
            if not isinstance(category_data["papers"], list):
                return False
        
        return True
    
    def highlight_words(self, text: str) -> str:
        """Highlight specified words in text."""
        highlight_words = self.config.get("highlights", {}).get("words", [])
        if not highlight_words:
            return text
        
        # Create regex pattern for all highlight words (case-insensitive)
        pattern = r'\b(' + '|'.join(re.escape(word) for word in highlight_words) + r')\b'
        
        def replace_match(match):
            return f'<span class="highlight">{match.group(0)}</span>'
        
        return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    
    def format_authors(self, authors: List[str]) -> str:
        """Format authors list with proper display."""
        if not authors:
            return ""
        
        max_authors = self.config["settings"]["max_authors_display"]
        if len(authors) <= max_authors:
            return ", ".join(authors)
        else:
            displayed = authors[:max_authors]
            return ", ".join(displayed) + ", et al."
    
    def generate_paper_html(self, paper: Dict[str, Any]) -> str:
        """Generate HTML for a single paper."""
        title = self.highlight_words(paper["title"])
        authors = self.format_authors(paper["display_authors"])
        
        # Format submission date
        submitted_date = datetime.fromisoformat(paper["submitted_date"])
        date_str = submitted_date.strftime("%Y-%m-%d")
        
        # Generate the DOI from the arXiv ID - standard format for arXiv DOIs
        arxiv_id = paper['id'].split('v')[0]  # Remove version number if present
        zotero_doi_url = f"https://www.zotero.org/save?type=doi&q=https://doi.org/10.48550/arXiv.{arxiv_id}"
        
        html = f'''
        <div class="paper">
            <div class="paper-header" onclick="togglePaper(this)">
                <span class="toggle-icon">▶</span>
                <div class="paper-title-section">
                    <h3 class="paper-title">{title}</h3>
                </div>
            </div>
            <div class="paper-content" style="display: none;">
                <div class="authors-section">
                    <h4>Authors</h4>
                    <div class="authors-with-links">
                        <p class="authors">{authors}</p>
                        <div class="paper-links">
                            <a href="{paper['arxiv_url']}" target="_blank" class="arxiv-link" title="View on ArXiv">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H6.9C4.01 7 1.9 9.11 1.9 12s2.11 5 5 5h4v-1.9H6.9c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9.1-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.89 0 5-2.11 5-5s-2.11-5-5-5z"/>
                                </svg>
                            </a>
                            <a href="{paper['pdf_url']}" target="_blank" class="pdf-link" title="Download PDF">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z M9,13V19H7V13H9M15,13V19H13V13H15M11,13V19H9V13H11"/>
                                </svg>
                            </a>
                            <a href="{zotero_doi_url}" target="_blank" class="zotero-link" title="Add to Zotero">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                                    <polygon points="13.863 2.73 13.027 1 2.137 1 2.137 3.8 2.137 3.921 8.822 3.921 1.289 13.233 2.137 15 13.863 15 13.863 12.142 13.863 12.021 6.448 12.021 13.863 2.73"/>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="abstract">
                    <h4>Abstract</h4>
                    <p>{paper['summary']}</p>
                </div>
                {f'<div class="comments">{paper["comments"]}</div>' if paper.get("comments") else ""}
                <div class="paper-info">
                    <span class="submitted-date">Submitted: {date_str}</span>
                    <span class="arxiv-id">ArXiv ID: {paper['id']}</span>
                </div>
            </div>
        </div>'''
        
        return html
    
    def generate_category_html(self, category_code: str, category_data: Dict[str, Any], expanded: bool = False) -> str:
        """Generate HTML for a category section."""
        category_name = category_data["name"]
        papers = category_data["papers"]
        paper_count = len(papers)
        icon_class = "toggle-icon expanded" if expanded else "toggle-icon"
        content_display = "block" if expanded else "none"
        category_class = "category-" + re.sub(r"[^a-z0-9]+", "-", category_code.lower()).strip("-")
        
        if paper_count == 0:
            return f'''
            <div class="category {category_class}">
                <div class="category-header" onclick="toggleCategory(this)">
                    <span class="{icon_class}">▶</span>
                    <h2>{category_name}</h2>
                    <span class="category-count">0 papers</span>
                </div>
                <div class="category-content" style="display: {content_display};">
                    <p class="no-papers">No papers found for this category today.</p>
                </div>
            </div>'''
        
        papers_html = ""
        for paper in papers:
            papers_html += self.generate_paper_html(paper)
        
        html = f'''
        <div class="category {category_class}">
            <div class="category-header" onclick="toggleCategory(this)">
                <span class="{icon_class}">▶</span>
                <h2>{category_name}</h2>
                <span class="category-count">{paper_count} {'paper' if paper_count == 1 else 'papers'}</span>
            </div>
            <div class="category-content" style="display: {content_display};">
                {papers_html}
            </div>
        </div>'''
        
        return html
    
    def copy_static_assets(self):
        """Copy CSS, JS, and favicon files from templates to output directory."""
        # Copy CSS file
        css_template = self.templates_dir / "style.css"
        css_output = self.output_dir / "css" / "style.css"
        if css_template.exists():
            shutil.copy2(css_template, css_output)
            print(f"Copied CSS: {css_template} -> {css_output}")
        
        # Copy JS file
        js_template = self.templates_dir / "script.js"
        js_output = self.output_dir / "js" / "script.js"
        if js_template.exists():
            shutil.copy2(js_template, js_output)
            print(f"Copied JS: {js_template} -> {js_output}")
        
        # Copy favicon
        favicon_template = self.templates_dir / "favicon.ico"
        favicon_output = self.output_dir / "favicon.ico"
        if favicon_template.exists():
            shutil.copy2(favicon_template, favicon_output)
            print(f"Copied favicon: {favicon_template} -> {favicon_output}")

    def generate_index_html(self) -> str:
        """Generate the main index.html file using template."""
        # Get all available data files - only valid JSON files
        data_files = self.get_valid_data_files()
        
        if not data_files:
            return self.generate_empty_page()
        
        # Get site configuration
        site_title = self.config["site"]["title"]
        site_description = self.config["site"]["description"]
        
        # Generate content for all dates
        all_dates_html = ""
        for i, file_path in enumerate(data_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate that the JSON has required structure
                if not self.validate_json_structure(data):
                    print(f"Warning: Skipping {file_path} - invalid JSON structure")
                    continue
                
                # Format the date
                current_date = datetime.fromisoformat(data["date"]).strftime("%Y-%m-%d")
                date_paper_count = sum(
                    len(category_data.get("papers", []))
                    for category_data in data["categories"].values()
                    if isinstance(category_data, dict)
                )
                is_latest_date = i == 0
                icon_class = "toggle-icon expanded" if is_latest_date else "toggle-icon"
                content_display = "block" if is_latest_date else "none"
                
                # Generate date header with toggle
                all_dates_html += f'<div class="date-section">\n'
                all_dates_html += f'    <div class="date-header" onclick="toggleDate(this)">\n'
                all_dates_html += f'        <span class="{icon_class}">▶</span>\n'
                all_dates_html += f'        <span class="date-label">{current_date}</span>\n'
                all_dates_html += f'        <span class="date-count">{date_paper_count} {"paper" if date_paper_count == 1 else "papers"}</span>\n'
                all_dates_html += f'    </div>\n'
                all_dates_html += f'    <div class="date-content" style="display: {content_display};">\n'
                
                # Generate categories for this date
                for category_code, category_data in data["categories"].items():
                    all_dates_html += self.generate_category_html(category_code, category_data, expanded=is_latest_date)
                
                all_dates_html += '    </div>\n'
                all_dates_html += '</div>\n'
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Skipping {file_path} - error reading file: {e}")
                continue
        
        # Get latest update time from the most recent file
        with open(data_files[0], 'r', encoding='utf-8') as f:
            latest_data = json.load(f)
        
        # Convert UTC time to CERN timezone (Europe/Zurich)
        utc_time = datetime.fromisoformat(latest_data["generated_at"]).replace(tzinfo=ZoneInfo('UTC'))
        cern_time = utc_time.astimezone(ZoneInfo('Europe/Zurich'))
        generated_at = cern_time.strftime("%Y-%m-%d %H:%M CET")
        
        # Load HTML template
        template_path = self.templates_dir / "index.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace template variables
        html = template.replace("{{ site_title }}", site_title)
        html = html.replace("{{ site_description }}", site_description)
        html = html.replace("{{ all_dates_content }}", all_dates_html)
        html = html.replace("{{ last_updated }}", generated_at)
        
        return html
    
    
    def generate_empty_page(self) -> str:
        """Generate a page when no data is available."""
        site_title = self.config["site"]["title"]
        site_description = self.config["site"]["description"]
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <meta name="description" content="{site_description}">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="stylesheet" href="css/style.css">
    
    <!-- KaTeX CSS and JS for fast LaTeX rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" integrity="sha384-GvrOXuhMATgEsSwCs4smul74iXGOixntILdUW9XmUC6+HX0sLNAK3q71HotJqlAn" crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js" integrity="sha384-cpW21h6RZv/phavutF+AuVYrr+dA8xD9zs6FwLpaCct6O9ctzYFfFr4dgmgccOTx" crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '$', right: '$', display: false}},
                    {{left: '\\\\(', right: '\\\\)', display: false}},
                    {{left: '\\\\[', right: '\\\\]', display: true}}
                ],
                throwOnError: false,
                errorColor: '#cc0000',
                macros: {{
                    "\\\\RR": "\\\\mathbb{{R}}",
                    "\\\\CC": "\\\\mathbb{{C}}",
                    "\\\\NN": "\\\\mathbb{{N}}",
                    "\\\\ZZ": "\\\\mathbb{{Z}}",
                    "\\\\QQ": "\\\\mathbb{{Q}}",
                    "\\\\dd": "\\\\mathrm{{d}}",
                    "\\\\ee": "\\\\mathrm{{e}}",
                    "\\\\ii": "\\\\mathrm{{i}}",
                    "\\\\ket": "\\\\left|#1\\\\right\\\\rangle",
                    "\\\\bra": "\\\\left\\\\langle#1\\\\right|",
                    "\\\\braket": "\\\\left\\\\langle#1\\\\right\\\\rangle",
                    "\\\\norm": "\\\\left\\\\|#1\\\\right\\\\|",
                    "\\\\abs": "\\\\left|#1\\\\right|",
                    "\\\\tr": "\\\\operatorname{{tr}}",
                    "\\\\Tr": "\\\\operatorname{{Tr}}",
                    "\\\\rank": "\\\\operatorname{{rank}}",
                    "\\\\span": "\\\\operatorname{{span}}",
                    "\\\\dim": "\\\\operatorname{{dim}}",
                    "\\\\det": "\\\\operatorname{{det}}",
                    "\\\\sgn": "\\\\operatorname{{sgn}}",
                    "\\\\diag": "\\\\operatorname{{diag}}",
                    "\\\\Re": "\\\\operatorname{{Re}}",
                    "\\\\Im": "\\\\operatorname{{Im}}",
                    "\\\\order": "\\\\mathcal{{O}}\\\\left(#1\\\\right)",
                    "\\\\bigO": "\\\\mathcal{{O}}\\\\left(#1\\\\right)",
                    "\\\\expect": "\\\\left\\\\langle#1\\\\right\\\\rangle",
                    "\\\\expectation": "\\\\mathbb{{E}}\\\\left[#1\\\\right]",
                    "\\\\var": "\\\\operatorname{{Var}}\\\\left[#1\\\\right]",
                    "\\\\prob": "\\\\mathbb{{P}}\\\\left(#1\\\\right)",
                    "\\\\given": "\\\\mid",
                    "\\\\defeq": "\\\\stackrel{{\\\\text{{def}}}}{{=}}",
                    "\\\\const": "\\\\text{{const}}",
                    "\\\\half": "\\\\frac{{1}}{{2}}",
                    "\\\\inv": "^{{-1}}",
                    "\\\\trans": "^{{\\\\top}}",
                    "\\\\adj": "^{{\\\\dagger}}",
                    "\\\\perp": "\\\\bot",
                    "\\\\parallel": "\\\\|",
                    "\\\\floor": "\\\\left\\\\lfloor#1\\\\right\\\\rfloor",
                    "\\\\ceil": "\\\\left\\\\lceil#1\\\\right\\\\rceil",
                    "\\\\set": "\\\\left\\\\{{#1\\\\right\\\\}}",
                    "\\\\card": "\\\\left|#1\\\\right|"
                }}
            }});
        }});
    </script>
</head>
<body>
    <header>
        <div class="container">
            <h1>{site_title}</h1>
            <p class="site-description">{site_description}</p>
        </div>
    </header>
    
    <main class="container">
        <div class="empty-state">
            <h2>No papers available yet</h2>
            <p>Papers will appear here once the daily fetch runs.</p>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>Data sourced from <a href="https://arxiv.org/" target="_blank">ArXiv.org</a></p>
        </div>
    </footer>
    
    <script src="js/script.js"></script>
</body>
</html>'''
    
    
    def generate_site(self):
        """Generate the complete static site."""
        print("Generating static site...")
        
        # Check if we have any valid data files
        valid_files = self.get_valid_data_files()
        if not valid_files:
            print("No valid JSON data files found. Generating empty site.")
        else:
            print(f"Found {len(valid_files)} valid data files")
        
        # Copy static assets from templates
        self.copy_static_assets()
        
        # Generate main index page with all dates
        index_html = self.generate_index_html()
        index_file = self.output_dir / "index.html"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"Generated index page: {index_file}")
        
        # No historical pages - everything is on the main index page
        
        print("Static site generation completed!")


def main():
    """Main function to generate the static site."""
    try:
        generator = SiteGenerator()
        generator.generate_site()
        print("Site generated successfully!")
        
    except Exception as e:
        print(f"Error generating site: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
