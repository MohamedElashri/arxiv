# ArXiv Daily Papers

A GitHub Pages-powered web application that automatically fetches and displays daily papers from ArXiv in specified categories. The app features a clean, responsive design with dark/light mode support and collapsible sections for easy browsing.

## Features

- **Automated Daily Updates**: GitHub Actions fetch new papers every day at 7:00 AM
- **Multiple Categories**: Support for various ArXiv categories (configurable)
- **Dark/Light Mode**: Toggle between themes with persistent preference
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Collapsible Interface**: Categories and papers can be expanded/collapsed
- **Direct Links**: Quick access to ArXiv page and PDF downloads
- **Keyword Highlighting**: Configurable word highlighting in paper titles
- **7-Day Retention**: Automatic cleanup of old data to manage storage
- **Manual Trigger**: Option to manually run the update process

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

## Project Structure

```
├── .github/workflows/          # GitHub Actions workflows
│   ├── update-papers.yml      # Daily paper fetching
│   └── pages.yml              # GitHub Pages deployment
├── scripts/                   # Python scripts
│   ├── arxiv_fetcher.py       # ArXiv API integration
│   └── generate_site.py       # Static site generator
├── site/                      # Generated static site
│   ├── css/style.css          # Responsive CSS with themes
│   ├── js/script.js           # Interactive JavaScript
│   └── index.html             # Generated HTML pages
├── data/                      # JSON data files (auto-generated)
├── config.toml                # Configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

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

## Customization

### Styling

Edit `site/css/style.css` to customize:
- Colors and themes
- Layout and spacing
- Typography
- Responsive breakpoints

### Functionality

Edit `site/js/script.js` to add:
- Search functionality
- Additional interactions
- Analytics tracking
- Custom features

### Data Processing

Edit `scripts/arxiv_fetcher.py` to:
- Add more paper metadata
- Implement custom filtering
- Add additional data sources

## Troubleshooting

### Papers Not Updating

1. Check GitHub Actions logs in the "Actions" tab
2. Verify ArXiv API is accessible
3. Check if rate limits are being hit (script includes delays)

### Site Not Deploying

1. Ensure GitHub Pages is enabled in repository settings
2. Check the 'site' folder for generated HTML files
🌐 You can open site/index.html in a browser to preview

### Missing Papers

- ArXiv submissions may take time to appear in API
- Some categories may have fewer papers on certain days (or none at all)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
