import requests
from bs4 import BeautifulSoup
import re

def bypass_hubcloud(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", # Updated to a recent Chrome User-Agent
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/", # Mimic coming from a search engine
        "DNT": "1", # Do Not Track header
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        # Step 1: Get initial page
        print(f"Attempting to fetch initial page: {url}")
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Initial page status: {r.status_code}")

        soup = BeautifulSoup(r.text, 'html.parser')

        # Step 2: Look for <a id="download">
        download_btn = soup.find("a", {"id": "download"})
        if not download_btn or not download_btn.get("href"):
            print("❌ Download button not found on the initial page.")
            return "❌ Download button not found."
        
        final_url = download_btn["href"]
        if not final_url.startswith("http"):
            final_url = "https://hubcloud.one" + final_url
        print(f"Found final URL: {final_url}")

        # Step 3: Visit the final_url page
        print(f"Attempting to fetch final page: {final_url}")
        r2 = requests.get(final_url, headers=headers, timeout=15)
        r2.raise_for_status()
        print(f"Final page status: {r2.status_code}")

        soup2 = BeautifulSoup(r2.text, 'html.parser')

        # Step 4: Find all links ending in .mkv
        all_links = soup2.find_all("a", href=True)
        for link in all_links:
            href = link["href"]
            if ".mkv" in href:
                if not href.startswith("http"):
                    href = "https://hubcloud.one" + href
                print(f"✅ MKV File URL found: {href}")
                return href
        
        print("❌ .mkv file not found in the second page.")
        return "❌ .mkv file not found in the second page."

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} for {e.request.url}")
        return f"❌ HTTP Error: {e.response.status_code} for {e.request.url}"
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return f"❌ Connection Error: {e}"
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        return f"❌ Timeout Error: {e}"
    except requests.exceptions.RequestException as e:
        print(f"❌ An unexpected request error occurred: {e}")
        return f"❌ An unexpected request error occurred: {e}"
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return f"❌ An unexpected error occurred: {e}"

# Example usage
link = "https://hubcloud.one/drive/kmj8atzuk8xzsum" # Use a known working link if possible
bypassed = bypass_hubcloud(link)
print("\nResult:", bypassed)
