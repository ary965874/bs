from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/bypass")
async def bypass_handler(request: Request):
    url = request.query_params.get("url")

    if not url or not url.startswith("http"):
        return JSONResponse(status_code=400, content={"error": "❌ Invalid or missing `url` parameter"})

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return JSONResponse(status_code=500, content={"error": f"❌ Failed to fetch page. Status {response.status_code}"})

        soup = BeautifulSoup(response.text, "html.parser")
        download_btn = soup.find("a", id="download")

        if download_btn and download_btn.get("href"):
            download_url = download_btn["href"]
            if not download_url.startswith("http"):
                download_url = "https://hubcloud.one" + download_url

            return JSONResponse(status_code=200, content={"success": True, "url": download_url})
        else:
            return JSONResponse(status_code=404, content={"error": "❌ Download link not found."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"❌ Error: {str(e)}"})
