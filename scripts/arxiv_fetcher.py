#!/usr/bin/env python3
"""
ArXiv paper fetcher script that queries the ArXiv API for papers in specified categories
and saves them to JSON files for static site generation.
"""

import json
import os
import sys
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import requests
import toml
import xml.etree.ElementTree as ET
from urllib.parse import quote


class ArXivFetcher:
    def __init__(self, config_path: str = "config.toml"):
        """Initialize the ArXiv fetcher with configuration."""
        self.config = toml.load(config_path)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # ArXiv API endpoint
        self.arxiv_api = "http://export.arxiv.org/api/query"
        
    def clean_old_data(self):
        """Keep only the last N days of data files (not calendar days, but actual files with data)."""
        retention_days = self.config["settings"]["retention_days"]
        
        # Create archive directory if it doesn't exist
        archive_dir = self.data_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        # Get all valid JSON files with dates
        valid_files = []
        for json_file in self.data_dir.glob("*.json"):
            try:
                # Extract date from filename (format: YYYY-MM-DD.json)
                date_str = json_file.stem
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                valid_files.append((file_date, json_file))
            except ValueError:
                # Skip files that don't match the expected date format
                continue
        
        # Sort by date (most recent first)
        valid_files.sort(key=lambda x: x[0], reverse=True)
        
        # Keep only the most recent retention_days files, archive the rest
        if len(valid_files) > retention_days:
            files_to_archive = valid_files[retention_days:]
            for _, json_file in files_to_archive:
                archive_path = archive_dir / json_file.name
                shutil.move(str(json_file), str(archive_path))
                print(f"Archived old data file: {json_file} -> {archive_path}")
    
    def fetch_papers_for_category(self, category: str, date_str: str) -> List[Dict[str, Any]]:
        """Fetch papers for a specific category and date."""
        # Format date for ArXiv query (YYYYMMDD)
        query_date = date_str.replace("-", "")
        
        # Build query parameters
        params = {
            "search_query": f"cat:{category} AND submittedDate:[{query_date}0000 TO {query_date}2359]",
            "start": 0,
            "max_results": self.config["settings"]["max_papers_per_category"],
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(self.arxiv_api, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            for entry in root.findall('atom:entry', namespaces):
                paper = self.parse_paper_entry(entry, namespaces)
                if paper:
                    papers.append(paper)
            
            print(f"Fetched {len(papers)} papers for category {category}")
            return papers
            
        except requests.RequestException as e:
            print(f"Error fetching papers for category {category}: {e}")
            return []
        except ET.ParseError as e:
            print(f"Error parsing XML response for category {category}: {e}")
            return []
    
    def parse_paper_entry(self, entry, namespaces) -> Dict[str, Any]:
        """Parse a single paper entry from ArXiv XML."""
        try:
            # Extract basic information
            title = entry.find('atom:title', namespaces).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', namespaces).text.strip().replace('\n', ' ')
            
            # Extract ArXiv ID and construct URLs
            arxiv_id = entry.find('atom:id', namespaces).text.split('/')[-1]
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', namespaces):
                name = author.find('atom:name', namespaces).text
                authors.append(name)
            
            # Limit authors display
            max_authors = self.config["settings"]["max_authors_display"]
            display_authors = authors[:max_authors]
            if len(authors) > max_authors:
                display_authors.append("et al.")
            
            # Extract submission date
            published = entry.find('atom:published', namespaces).text
            submitted_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            
            # Extract categories
            categories = []
            for category in entry.findall('atom:category', namespaces):
                categories.append(category.get('term'))
            
            # Extract comments if available
            comments = ""
            comment_elem = entry.find('arxiv:comment', namespaces)
            if comment_elem is not None:
                comments = comment_elem.text.strip()
            
            return {
                "id": arxiv_id,
                "title": title,
                "authors": authors,
                "display_authors": display_authors,
                "summary": summary,
                "arxiv_url": arxiv_url,
                "pdf_url": pdf_url,
                "submitted_date": submitted_date.isoformat(),
                "categories": categories,
                "comments": comments
            }
            
        except Exception as e:
            print(f"Error parsing paper entry: {e}")
            return None
    
    def fetch_daily_papers(self, target_date: str = None):
        """Fetch papers for all configured categories for a specific date."""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"Fetching papers for date: {target_date}")
        
        daily_data = {
            "date": target_date,
            "generated_at": datetime.now().isoformat(),
            "categories": {}
        }
        
        total_papers = 0
        
        # Fetch papers for each category
        for category_code, category_name in self.config["categories"].items():
            print(f"Fetching papers for category: {category_name} ({category_code})")
            
            papers = self.fetch_papers_for_category(category_code, target_date)
            
            daily_data["categories"][category_code] = {
                "name": category_name,
                "papers": papers,
                "count": len(papers)
            }
            
            total_papers += len(papers)
            
            # Rate limiting to be respectful to ArXiv API
            time.sleep(3)
        
        # Check if any papers were found across all categories
        if total_papers == 0:
            print(f"No papers found for any category on {target_date}. Skipping JSON file creation.")
            return None
        
        # Save to JSON file only if papers were found
        output_file = self.data_dir / f"{target_date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {total_papers} papers to: {output_file}")
        
        # Clean up old data
        self.clean_old_data()
        
        return daily_data


def main():
    """Main function to run the ArXiv fetcher."""
    # Allow specifying a date as command line argument
    target_date = None
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    
    try:
        fetcher = ArXivFetcher()
        fetcher.fetch_daily_papers(target_date)
        print("ArXiv papers fetched successfully!")
        
    except Exception as e:
        print(f"Error running ArXiv fetcher: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
