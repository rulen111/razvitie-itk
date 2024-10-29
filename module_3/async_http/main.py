import asyncio
import aiohttp
import json

CONCURRENT_REQUESTS = 5

URLS = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://google.com",
]


async def fetch(url: str, session: aiohttp.ClientSession) -> int:
    """
    Fetch single url using session
    :param url: string url address
    :param session: aiohttp.ClientSession object
    :return: status code
    """
    try:
        async with session.get(url) as resp:
            return resp.status
    except aiohttp.ClientConnectorError:
        return 0
    except asyncio.TimeoutError:
        return 1
    except aiohttp.InvalidURL:
        return 2
    except aiohttp.ContentTypeError:
        return 3


async def sem_fetch(sem: asyncio.Semaphore, url: str, session: aiohttp.ClientSession, outfile) -> None:
    """
    Bind fetch function to semaphore
    :param sem: asyncio.Semaphore object
    :param url: string url address
    :param session: aiohttp.ClientSession object
    :param outfile: file-like outfile
    :return: None
    """
    async with sem:
        status = await fetch(url, session)
        result = {"url": url, "status_code": status}
        json.dump(result, outfile)
        outfile.write("\n")


async def fetch_urls(urls: list[str], file_path: str) -> None:
    """
    Run fetching for url list
    :param urls: list of string url addresses
    :param file_path: outfile path
    :return: None
    """
    tasks = []
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    with open(file_path, "a") as f:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                task = asyncio.create_task(sem_fetch(sem, url, session, f))
                tasks.append(task)
            await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(fetch_urls(URLS, './results.jsonl'))
