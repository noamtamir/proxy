from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import os

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    headers = dict(response.headers)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=headers
    )
