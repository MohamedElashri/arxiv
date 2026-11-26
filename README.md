# AI Papers Daily

A daily arXiv reader for agentic systems, AI engineering, and broader AI research. A local model groups papers by their contribution, and Nida builds the site.

## Run locally

Use Python 3.11 or 3.12 and [Nida 0.8.5](https://github.com/MohamedElashri/nida).

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/prepare_feed.py
nida serve
```

Preview at [localhost:1702/arxiv/](http://127.0.0.1:1702/arxiv/). The first run downloads the embedding model. Edit [config.toml](config.toml) to change arXiv categories or topic definitions.

## Update papers

GitHub Actions fetches and publishes the feed daily. To fetch a specific submission date and build locally, run the following commands.

```bash
python scripts/arxiv_fetcher.py YYYY-MM-DD
python scripts/prepare_feed.py
nida build
```

Run `ARXIV_TEST_MODEL=1 python -m unittest discover -s tests` to check the discovery model.

Licensed under the MIT License.
