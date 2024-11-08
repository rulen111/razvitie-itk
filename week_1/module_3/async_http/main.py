import asyncio
import time
import aiohttp
import json

# Number of high level coroutines to start concurrently
NUMBER_OF_WORKERS = 10

# URLS = [
#     "https://example.com",
#     "https://httpbin.org/status/404",
#     "https://nonexistent.url",
#     "https://httpbin.org/status/200",
#     "https://httpbin.org/status/500",
#     "https://google.com",
# ]
URLS = [f"https://httpbin.org/status/{code}" for code in range(200, 600)]


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


async def populate_queue(input_queue: asyncio.Queue, urls: list[str]) -> None:
    """
    Populate input queue with values and add None at the end to stop workers
    :param input_queue: asyncio.Queue for urls
    :param urls: list of string url addresses to be fetched
    :return: None
    """
    for url in urls:
        await input_queue.put(url)

    for _ in range(NUMBER_OF_WORKERS):
        await input_queue.put(None)


async def fetch_urls(input_queue: asyncio.Queue, output_queue: asyncio.Queue, session: aiohttp.ClientSession) -> None:
    """
    Start fetching urls from input queue and writing results to output queue
    :param input_queue: asyncio.Queue populated with urls
    :param output_queue: asyncio.Queue for fetching results
    :param session: aiohttp.ClientSession for making requests
    :return: None
    """
    while True:
        url = await input_queue.get()
        if url is None:
            await output_queue.put(None)
            break
        else:
            status = await fetch(url, session)
            result = {"url": url, "status_code": status}
            await output_queue.put(result)


async def write_results(input_queue: asyncio.Queue, outfile) -> None:
    """
    Start writing results to output file line by line
    :param input_queue: asyncio.Queue populated with fetching results
    :param outfile: file-like object to write to
    :return: None
    """
    while True:
        line = await input_queue.get()
        if line is None:
            break
        else:
            json.dump(line, outfile)
            outfile.write("\n")


async def main():
    print(f"Processing {len(URLS)} urls...")
    t_start = time.perf_counter()

    input_queue = asyncio.Queue(len(URLS))
    output_queue = asyncio.Queue(len(URLS))

    with open("results.jsonl", "a") as f:
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(populate_queue(input_queue, URLS))]
            for i in range(NUMBER_OF_WORKERS):
                tasks += [
                    asyncio.create_task(fetch_urls(input_queue, output_queue, session)),
                    asyncio.create_task(write_results(output_queue, f))
                ]

            await asyncio.gather(*tasks)

    exec_time = time.perf_counter() - t_start
    print(f"Done in {exec_time} seconds")


if __name__ == '__main__':
    asyncio.run(main())
