import argparse
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

def crawl_domain(start_url, max_pages=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    domain = urlparse(start_url).netloc
    visited = set()
    queue = [start_url]
    all_data = []
    
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
            
        print(f"Crawling: {url}")
        visited.add(url)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract detailed elements
            title = soup.title.string if soup.title else ""
            
            headings = {}
            for i in range(1, 7):
                tags = soup.find_all(f'h{i}')
                if tags:
                    headings[f"h{i}"] = [tag.get_text(strip=True) for tag in tags]
                    
            # Extract meta descriptions and keywords
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')
                
            # Clean text
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            text = soup.get_text(separator='\n')
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(chunk for chunk in (phrase.strip() for line in lines for phrase in line.split("  ")) if chunk)
            
            # Get links
            links = []
            for a in soup.find_all('a', href=True):
                if not a.has_attr('href'):
                    continue
                href = a['href']
                full_url = urljoin(url, href)
                links.append({"text": a.text.strip(), "url": full_url})
                
                # Add to queue if same domain
                if urlparse(full_url).netloc == domain and full_url not in visited and full_url not in queue:
                    queue.append(full_url)
                    
            all_data.append({
                "url": url,
                "title": title.strip(),
                "meta_description": meta_desc,
                "headings": headings,
                "content": clean_text,
                "links": links
            })
            
            time.sleep(1) # Be respectful
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            
    return all_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extensive Web Crawler/Scraper")
    parser.add_argument("--url", required=True, help="Starting URL to scrape")
    parser.add_argument("--max_pages", type=int, default=10, help="Maximum pages to crawl within the domain")
    parser.add_argument("--output", default="web_results.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    print(f"Starting extensive crawl from {args.url} (max pages: {args.max_pages})...")
    data = crawl_domain(args.url, args.max_pages)
    
    if data:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully crawled {len(data)} pages. Saved to {args.output}")
    else:
        print("Scraping failed.")
