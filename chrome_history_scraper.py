import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from datetime import datetime
import json

def get_chrome_history_path():
    """Get the path to Chrome's history database."""
    # Default Chrome history path for Windows
    app_data = os.getenv('LOCALAPPDATA')
    return os.path.join(app_data, 'Google', 'Chrome', 'User Data', 'Default', 'History')

def get_history_urls(limit=100):
    """Extract URLs from Chrome history."""
    history_path = get_chrome_history_path()
    if not os.path.exists(history_path):
        raise FileNotFoundError("Chrome history database not found. Make sure Chrome is closed.")
    
    # Create a copy of the history file since Chrome locks it
    temp_path = 'temp_history'
    with open(history_path, 'rb') as src, open(temp_path, 'wb') as dst:
        dst.write(src.read())
    
    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    
    # Query to get recent URLs
    query = """
    SELECT urls.url, urls.title, urls.last_visit_time
    FROM urls
    ORDER BY urls.last_visit_time DESC
    LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    urls = cursor.fetchall()
    
    conn.close()
    os.remove(temp_path)
    
    return urls

def extract_text_from_url(url):
    """Extract text content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def main():
    try:
        # Get URLs from history
        print("Extracting URLs from Chrome history...")
        urls = get_history_urls(limit=100)  # Adjust limit as needed
        
        # Create output directory
        output_dir = "scraped_texts"
        os.makedirs(output_dir, exist_ok=True)
        
        # Scrape text from each URL
        results = []
        for url, title, visit_time in tqdm(urls, desc="Scraping websites"):
            # Convert Chrome timestamp to readable format
            visit_time = datetime(1601, 1, 1) + time.timedelta(microseconds=visit_time)
            
            print(f"\nProcessing: {url}")
            text = extract_text_from_url(url)
            
            # Save individual file
            filename = f"{output_dir}/{title[:50]}_{visit_time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Title: {title}\n")
                f.write(f"Visit Time: {visit_time}\n\n")
                f.write(text)
            
            results.append({
                'url': url,
                'title': title,
                'visit_time': visit_time.strftime('%Y-%m-%d %H:%M:%S'),
                'text_file': filename
            })
            
            # Add delay to be respectful to servers
            time.sleep(1)
        
        # Save summary
        with open(f"{output_dir}/summary.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nScraping completed! Results saved in '{output_dir}' directory.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 