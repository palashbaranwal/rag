# Chrome History Text Extractor

This script extracts text content from websites in your Chrome browsing history.

## Prerequisites

- Python 3.6 or higher
- Chrome browser installed
- Chrome must be closed while running the script

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Close Chrome browser completely
2. Run the script:
```bash
python chrome_history_scraper.py
```

The script will:
- Extract the 100 most recent URLs from your Chrome history
- Scrape text content from each URL
- Save the extracted text in individual files in the `scraped_texts` directory
- Create a summary file (`summary.json`) with metadata about all scraped pages

## Output

- Each webpage's content is saved as a separate text file in the `scraped_texts` directory
- Files are named using the page title and visit time
- A `summary.json` file contains metadata about all scraped pages

## Notes

- The script includes a 1-second delay between requests to be respectful to servers
- Some websites might block scraping attempts
- The script handles errors gracefully and will continue with the next URL if one fails
- By default, it processes the 100 most recent URLs from your history 