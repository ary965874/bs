# main.py

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

# Root health check endpoint (required by Koyeb)
@app.get("/")
def health():
    return {"status": "running"}

def bypass_hubcloud(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
    except Exception:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    download_btn = soup.find("a", {"id": "download"})
    if not download_btn or not download_btn.get("href"):
        return None

    final_url = download_btn["href"]
    if not final_url.startswith("http"):
        final_url = "https://hubcloud.one" + final_url

    try:
        r2 = requests.get(final_url, headers=headers, timeout=10)
        if r2.status_code != 200:
            return None
    except Exception:
        return None

    soup2 = BeautifulSoup(r2.text, 'html.parser')
    for a in soup2.find_all("a", href=True):
        href = a["href"]
        if ".mkv" in href:
            if not href.startswith("http"):
                href = "https://hubcloud.one" + href
            return href
    return None

@app.get("/api/post")
async def fetch_post(url: str = Query(..., description="Post URL to scrape and bypass")):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return JSONResponse({"error": f"Failed to fetch page. Status: {res.status_code}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": "Fetch error", "details": str(e)}, status_code=500)

    soup = BeautifulSoup(res.text, 'html.parser')

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    image = None
    img_tag = soup.select_one("div.entry-content img, img.aligncenter")
    if img_tag:
        image = img_tag.get("src")

    stream_url = None
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"]
        if "watch" in text and "hdstream" in href:
            stream_url = href
            break

    download_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text()
        if "hubdrive.space/file/" in href:
            match = re.search(r"(1080p|720p|480p|360p)", text, re.I)
            if match:
                quality = match.group(1)
                file_id = href.strip("/").split("/")[-1]
                drive_url = f"https://hubcloud.one/drive/{file_id}"
                bypassed = bypass_hubcloud(drive_url)
                download_links.append({
                    "name": quality,
                    "original": href,
                    "direct": bypassed or "❌ Failed"
                })

    return {
        "title": title,
        "image": image,
        "streamUrl": stream_url,
        "bypassedLinks": download_links
    }
