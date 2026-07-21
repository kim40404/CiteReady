import httpx
import asyncio

async def test():
    urls = [
        "https://www.python.org/about/",
        "https://plato.stanford.edu/entries/turing-test/"
    ]
    async with httpx.AsyncClient(timeout=30) as client:
        for url in urls:
            res = await client.post('http://localhost:8000/api/v1/analyze', json={'url': url})
            if res.status_code == 200:
                data = res.json()
                print(f"URL: {url} | Grade: {data.get('grade')} | Score: {data.get('geo_score')}")
            else:
                print(f"URL: {url} | Error: {res.status_code} {res.text}")

if __name__ == "__main__":
    asyncio.run(test())
