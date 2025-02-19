import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import os

logging.basicConfig(level=logging.INFO)

app = FastAPI()

API_KEY = os.getenv("API_KEY")


class ProxyRequest(BaseModel):
    url: str


@app.post("/proxy")
async def proxy(request: Request, proxy_request: ProxyRequest):
    url = proxy_request.url

    # Verify API key
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Add common browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": "\"Not(A':B'rand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\""
    }
    logging.info(f"Proxying request to {url}")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)

    headers = dict(response.headers)
    logging.info(f"Request actual headers: {response.request.headers}")
    logging.info(f"Response headers: {headers}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=headers
    )
