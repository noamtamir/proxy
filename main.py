import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Any

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# TODO: Update CORS settings before deploying to production
# Currently allowing all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

API_KEY = os.getenv("API_KEY")

@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    # Verify API key
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Get the full URL including query parameters
    url = f"{path}{'?' + str(request.query_params) if request.query_params else ''}"
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Get the original request method
    method = request.method

    # Start with default browser headers
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

    # Update headers with the original request Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    logging.info(f"Proxying {method} request to {url}")

    # Get the request body for methods that might have one
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        body = await request.body()

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            content=body,
            follow_redirects=True
        )

    headers = dict(response.headers)
    logging.info(f"Request actual headers: {response.request.headers}")
    logging.info(f"Response headers: {headers}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=headers
    )
