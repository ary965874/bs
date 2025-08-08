# main.py
import requests
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Hubcloud Bypass API",
    description="API to bypass Hubcloud links and extract .mkv file URLs.",
    version="1.0.0",
)

def bypass_hubcloud_logic(url: str):
    """
    Bypasses the Hubcloud link to find the direct .mkv file URL.
    Returns a dictionary with 'success' status and either 'mkv_url' or 'message'.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", # Updated Chrome version
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/", # Add a common referer
        "DNT": "1", # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Step 1: Get initial page
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Step 2: Look for <a id="download">
        download_btn = soup.find("a", {"id": "download"})
        if not download_btn or not download_btn.get("href"):
            return {"success": False, "message": "Download button not found on the initial page."}
        
        final_url = download_btn["href"]
        # Ensure the URL is absolute
        if not final_url.startswith("http"):
            # This assumes the base domain is hubcloud.one, adjust if necessary
            final_url = "https://hubcloud.one" + final_url 
        
        # Step 3: Visit the final_url page
        r2 = requests.get(final_url, headers=headers, timeout=15)
        r2.raise_for_status()
        
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        
        # Step 4: Find all links ending in .mkv
        all_links = soup2.find_all("a", href=True)
        for link in all_links:
            href = link["href"]
            if ".mkv" in href:
                if not href.startswith("http"):
                    href = "https://hubcloud.one" + href
                return {"success": True, "mkv_url": href}
        
        return {"success": False, "message": ".mkv file not found on the second page."}
        
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Network or HTTP error during request: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {e}"}

@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Hubcloud Bypass API! Use /bypass?url=<your_hubcloud_url> to get the .mkv link."}

@app.get("/bypass")
async def get_bypassed_url(url: str):
    """
    Bypasses a Hubcloud URL to find the direct .mkv file link.
    
    - **url**: The Hubcloud URL to bypass (e.g., `https://hubcloud.one/drive/kmj8atzuk8xzsum`).
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required.")
    
    result = bypass_hubcloud_logic(url)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return JSONResponse(content=result)
