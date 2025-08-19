import aiohttp
from python.helpers import runtime

URL = "http://localhost:55510/search"

async def search(query:str):
    # Direct call instead of RFC routing since SearXNG runs on different port
    return await _search(query)

async def _search(query:str):
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data={"q": query, "format": "json"}) as response:
            return await response.json()
