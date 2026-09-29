import argparse
import requests
import json
import time
import base64

def search_github(query, limit):
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={min(limit, 100)}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    results = []
    page = 1
    
    while len(results) < limit:
        try:
            paged_url = f"{url}&page={page}"
            response = requests.get(paged_url, headers=headers)
            
            if response.status_code == 403:
                print("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue
                
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            for item in items:
                if len(results) >= limit:
                    break
                repo_full_name = item.get("full_name")
                print(f"Deep scraping: {repo_full_name}")
                
                # Fetch detailed parts
                readme_content = fetch_readme(repo_full_name, headers)
                tree = fetch_tree(repo_full_name, item.get("default_branch"), headers)
                
                repo_info = {
                    "name": repo_full_name,
                    "description": item.get("description"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "language": item.get("language"),
                    "topics": item.get("topics", []),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "readme": readme_content,
                    "file_tree": tree, # the full structure
                }
                results.append(repo_info)
                time.sleep(1) # Be nice to the API
                
            page += 1
        except Exception as e:
            print(f"Error searching for {query}: {e}")
            break
            
    return results

def fetch_readme(repo_full_name, headers):
    try:
        readme_url = f"https://api.github.com/repos/{repo_full_name}/readme"
        resp = requests.get(readme_url, headers=headers)
        if resp.status_code == 200:
            content = resp.json().get('content', '')
            return base64.b64decode(content).decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def fetch_tree(repo_full_name, branch, headers):
    try:
        tree_url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{branch}?recursive=1"
        resp = requests.get(tree_url, headers=headers)
        if resp.status_code == 200:
            return [file.get("path") for file in resp.json().get("tree", []) if file.get("type") == "blob"]
    except Exception:
        pass
    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extensive GitHub Scraper")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of repos to fetch")
    parser.add_argument("--output", default="github_results.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    print(f"Scraping GitHub for '{args.query}' (limit: {args.limit})...")
    data = search_github(args.query, args.limit)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Scraped {len(data)} repositories extensively. Results saved to {args.output}")
