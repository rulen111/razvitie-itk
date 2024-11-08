import random
import os
import time
import csv
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue


def generate_data(n: int = 1) -> list[int]:
    """
    Generates a list of n random integers between 1 and 1000
    :param n: hom many numbers to return
    :return: list containing random n numbers
    """
    result = []
    for _ in range(n):
        result.append(random.randint(1, 1000))

    return result


def process_number(number: int) -> int:
    """
    Check if a number is prime. O(n) instead of O(n**0.5) for the sake of heavy computation
    :param number: number to check
    :return: True or False
    """
    if number > 1:
        # for i in range(2, int(math.sqrt(number)) + 1):
        for i in range(2, int(number // 2) + 1):
            if (number % i) == 0:
                return 0
        return 1
    else:
        return 0


def get_task_queue(numbers: list[int]) -> Queue:
    """
    Populate task queue
    :param numbers: list of numbers
    :return: Queue object
    """
    task_queue = Queue()
    for number in numbers:
        task_queue.put(number)
    return task_queue


def worker(input: Queue, output: Queue) -> None:
    """
    Multiprocessing worker
    :param input: Queue object with input data
    :param output: Queue object with output data
    :return: None
    """
    for num in iter(input.get, "STOP"):
        result = process_number(num)
        output.put(result)


def time_func(func, *args, **kwargs):
    """
    Calculates func execution time
    :param func: function to time
    :param args: function args
    :param kwargs: function kwargs
    :return: execution time and func return
    """
    t_start = time.perf_counter()
    result = func(*args, **kwargs)
    all_time = time.perf_counter() - t_start
    return all_time, result


def run_single_thread(numbers: list[int]) -> list[int]:
    """
    Run number processing in a single thread
    :param numbers: list of numbers
    :return: list of numbers (0, 1)
    """
    results = []
    for number in numbers:
        results.append(process_number(number))

    return results


def run_tpe(numbers: list[int]) -> list[int]:
    """
    Run number processing in ThreadPoolExecutor
    :param numbers: list of numbers
    :return: list of numbers (0, 1)
    """
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        results = list(executor.map(process_number, numbers))

    return results


def run_mp_pool(numbers: list[int]) -> list[int]:
    """
    Run number processing in multiprocessing.Pool
    :param numbers: list of numbers
    :return: list of numbers (0, 1)
    """
    with Pool(os.cpu_count()) as pool:
        results = list(pool.map(process_number, numbers))

    return results


def run_mp_process(numbers: list[int]) -> list[int]:
    """
    Run number processing in multiprocessing.Process
    :param numbers: list of numbers
    :return: list of numbers (0, 1)
    """
    task_queue = get_task_queue(numbers)
    done_queue = Queue()
    results = []

    for i in range(os.cpu_count()):
        Process(target=worker, args=(task_queue, done_queue)).start()

    for i in range(len(numbers)):
        results.append(done_queue.get())

    for i in range(os.cpu_count()):
        task_queue.put('STOP')

    return results


def write_results(results: list, fp: str) -> None:
    """
    Write results to a csv file
    :param results: list of results
    :param fp: filepath for writing
    :return: None
    """
    with open(fp, "w", newline="") as csvfile:
        fieldnames = [
            "number", "Single Thread", "ThreadPoolExecutor", "multiprocessing_Pool", "multiprocessing_Process_Queue"
        ]
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for row in results:
            writer.writerow(row)


def test_perf(count: int) -> (list, list):
    """
    Test performance of all methods for a specific amount of numbers to process
    :param count: amount of numbers to process
    :return: a list with resulting data and a list with execution times
    """
    print("-" * 24)
    print("Generating numbers...")
    numbers_list = generate_data(count)
    print(f"Success! Generated {len(numbers_list)} numbers.", "\n--")
    perf_log = list()

    all_result = []
    for func in [run_single_thread, run_tpe, run_mp_pool, run_mp_process]:
        print(f"Starting processing using {func.__name__}...")
        all_time, results = time_func(func, numbers_list)
        perf_log.append(all_time)
        all_result.append(results)
        print(f"Success! Processed {len(results)} numbers using {func.__name__} in {all_time} seconds.", "\n--")

    data = zip(numbers_list, *all_result)

    return data, perf_log


if __name__ == "__main__":
    performance = []
    count_range = [10 ** i for i in range(1, 7)]
    for count in count_range:
        data, perf = test_perf(count)
        performance.append(perf)
        write_results(data, f"data/res_{count}.csv")

    perf_data = [[num, *line] for num, line in zip(count_range, performance)]
    write_results(perf_data, "data/performance.csv")

    performance_t = list(zip(*performance))
    names = ["Single Thread", "ThreadPoolExecutor", "multiprocessing_Pool", "multiprocessing_Process_Queue"]
    x = count_range
    fig, ax = plt.subplots()
    for name, y in zip(names, performance_t):
        ax.plot(x, y, label=name)
    ax.legend()
    plt.show()
