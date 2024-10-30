import asyncio
import time
import aiohttp
import json

CONCURRENT_REQUESTS = 10
NUMBER_OF_WORKERS = 10

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


async def worker(queue: asyncio.Queue, sem: asyncio.Semaphore, session: aiohttp.ClientSession, outfile) -> None:
    """
    Coroutine to consume work
    :param queue: asyncio.Queue object with urls to be processed
    :param sem: asyncio.Semaphore object
    :param session: aiohttp.ClientSession object
    :param outfile: file-like outfile
    :return: None
    """
    while True:
        url = await queue.get()
        await sem_fetch(sem, url, session, outfile)
        queue.task_done()


async def fetch_urls(urls: list[str], file_path: str) -> None:
    """
    Run fetching for url list
    :param urls: list of string url addresses
    :param file_path: outfile path
    :return: None
    """
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    queue = asyncio.Queue()
    for url in urls:
        queue.put_nowait(url)

    with open(file_path, "a") as f:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(NUMBER_OF_WORKERS):
                task = asyncio.create_task(worker(queue, sem, session, f))
                tasks.append(task)

            await queue.join()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    # asyncio.run(fetch_urls(URLS, './results.jsonl'))
    urls = [f"https://httpbin.org/status/{code}" for code in range(200, 600)]
    print(f"Processing {len(urls)} urls...")
    t_start = time.perf_counter()
    asyncio.run(fetch_urls(urls, './results.jsonl'))
    exec_time = time.perf_counter() - t_start
    print(f"Done in {exec_time} seconds")
