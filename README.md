# ArXiv Daily Papers

A GitHub Pages-powered web application that automatically fetches and displays daily papers from ArXiv in specified categories. The app features a clean, responsive design with dark/light mode support and collapsible sections for easy browsing.

## Setup Instructions

### 1. Fork/Clone this Repository

```bash
git clone https://github.com/MohamedElashri/arxiv
cd arxiv
```

### 2. Configure Categories and Settings

Edit `config.toml` to customize:

```toml
[categories]
# Add your desired ArXiv categories
hep-ex = "High Energy Physics - Experiment"
hep-ph = "High Energy Physics - Phenomenology"
# Add more categories as needed

[highlights]
# Words to highlight in paper titles
words = ["quantum", "machine learning", "neural"]

[site]
title = "ArXiv Daily Papers"
description = "Daily collection of papers from ArXiv in selected categories"
```

### 3. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages" section
3. Set source to "GitHub Actions"
4. The site will be available at `https://<your-username>.github.io/repository-name`

### 4. Set Up GitHub Actions

The workflows are already configured and will:
- Run daily at 7:00 AM UTC (adjust timezone in `config.toml`)
- Allow manual triggering from the Actions tab
- Automatically deploy to GitHub Pages

### 5. First Run

To populate your site with initial data:
1. Go to the "Actions" tab in your repository
2. Select "Update ArXiv Papers" workflow
3. Click "Run workflow" to trigger manually

## Configuration Options

### Categories

Add ArXiv category codes and display names in `config.toml`:

```toml
[categories]
hep-ex = "High Energy Physics - Experiment"
astro-ph = "Astrophysics"
gr-qc = "General Relativity and Quantum Cosmology"
```

Common ArXiv categories:
- `hep-ex`: High Energy Physics - Experiment
- `hep-ph`: High Energy Physics - Phenomenology  
- `hep-th`: High Energy Physics - Theory
- `astro-ph`: Astrophysics
- `gr-qc`: General Relativity and Quantum Cosmology
- `quant-ph`: Quantum Physics
- `cond-mat`: Condensed Matter
- `cs.AI`: Artificial Intelligence
- `cs.LG`: Machine Learning

### Highlighting

Configure words to highlight in paper titles:

```toml
[highlights]
words = ["quantum", "machine learning", "neural", "dark matter"]
```

### Site Settings

```toml
[site]
title = "My ArXiv Daily"
description = "Daily collection of papers from ArXiv"
base_url = "https://<your-username>.github.io/arxiv"

[settings]
retention_days = 7              # Days to keep old papers
max_papers_per_category = 50    # Max papers per category per day
max_authors_display = 3         # Show first N authors
```

## Usage

### Viewing Papers

- **Categories**: Click category headers to expand/collapse
- **Papers**: Click paper titles to view abstract and details
- **Links**: Use the icons next to author names to:
  - 📄 View paper on ArXiv
  - 📁 Download PDF directly

### Theme Toggle

- Click the theme button (🌙/☀️) in the header
- Theme preference is saved in browser localStorage
- Supports system theme detection

### Keyboard Shortcuts

- `Ctrl/Cmd + D`: Toggle theme
- `Escape`: Collapse all sections

## Manual Operations

### Fetch Papers for Specific Date

```bash
python scripts/arxiv_fetcher.py 2024-01-15
```

### Generate Site Locally

```bash
python scripts/generate_site.py
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## License

This project is open source and available under the [MIT License](LICENSE).
