import asyncio
import aiohttp
import json

CONCURRENT_REQUESTS = 5

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]


async def fetch_urls(urls: list[str], file_path: str):
    result = list()
    async with asyncio.Semaphore(CONCURRENT_REQUESTS):
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url) as resp:
                        result.append({"url": url, "status_code": resp.status})
                except aiohttp.ClientConnectorError:
                    result.append({"url": url, "status_code": 0})
                except asyncio.TimeoutError:
                    result.append({"url": url, "status_code": 1})
                except aiohttp.InvalidURL:
                    result.append({"url": url, "status_code": 2})
                except aiohttp.ContentTypeError:
                    result.append({"url": url, "status_code": 3})

    with open(file_path, "w") as f:
        json.dump({"results": result}, f, indent=4)

    return file_path


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.json'))
