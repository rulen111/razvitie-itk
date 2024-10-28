import math
import random
import os
import time
import csv
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


def process_number(number: int) -> bool:
    """
    Check if a number is prime
    :param number: number to check
    :return: True or False
    """
    if number > 1:
        for i in range(2, int(math.sqrt(number)) + 1):
            if (number % i) == 0:
                return False
        return True
    else:
        return False


def get_task_queue(numbers: list[int]) -> Queue:
    task_queue = Queue()
    for number in numbers:
        task_queue.put(number)
    return task_queue


def worker(input: Queue, output: Queue) -> None:
    for num in iter(input.get, "STOP"):
        result = process_number(num)
        output.put(result)


def run_single_thread(numbers: list[int]) -> list[bool]:
    results = []
    for number in numbers:
        results.append(process_number(number))

    return results


def run_tpe(numbers: list[int]) -> list[bool]:
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        results = list(executor.map(process_number, numbers))

    return results


def run_mp_pool(numbers: list[int]) -> list[bool]:
    with Pool(os.cpu_count()) as pool:
        results = list(pool.map(process_number, numbers))

    return results


def run_mp_process(numbers: list[int]) -> list[bool]:
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


# def write_results(results: dict, fp: str) -> None:
#     with open(fp, "w", newline="") as csvfile:
#         fieldnames = [
#             "number", "Single Thread", "ThreadPoolExecutor", "multiprocessing_Pool", "multiprocessing_Process_Queue"
#         ]
#         writer = csv.writer(csvfile)



def test_perf(count: int) -> dict:
    # print("-" * 24)
    # print("Generating numbers...")
    # numbers_list = generate_data(count)
    # print(f"Success! Generated {len(numbers_list)} numbers.\n")
    # results = {"count": count}
    #
    # print("Starting processing using single thread...")
    # t_start = time.perf_counter()
    # results_st = []
    # for number in numbers_list:
    #     results_st.append(process_number(number))
    # all_time = time.perf_counter() - t_start
    # print(f"Success! Processed {len(results_st)} numbers using single thread in {all_time} seconds.\n")
    # results["Single Thread"] = all_time
    #
    # print("Starting processing using ThreadPoolExecutor...")
    # t_start = time.perf_counter()
    # with ThreadPoolExecutor(os.cpu_count()) as executor:
    #     results_tpe = list(executor.map(process_number, numbers_list))
    # all_time = time.perf_counter() - t_start
    # print(f"Success! Processed {len(results_tpe)} numbers using TPE in {all_time} seconds.\n")
    # results["ThreadPoolExecutor"] = all_time
    #
    # print("Starting processing using multiprocessing.Pool...")
    # t_start = time.perf_counter()
    # with Pool(os.cpu_count()) as pool:
    #     results_mppool = list(pool.map(process_number, numbers_list))
    # all_time = time.perf_counter() - t_start
    # print(f"Success! Processed {len(results_mppool)} numbers using mp.Pool in {all_time} seconds.\n")
    # results["multiprocessing_Pool"] = all_time
    #
    # task_queue = Queue()
    # done_queue = Queue()
    # for number in numbers_list:
    #     task_queue.put(number)
    # print("Starting processing using Process and Queue...")
    # t_start = time.perf_counter()
    # for i in range(os.cpu_count()):
    #     Process(target=worker, args=(task_queue, done_queue)).start()
    # count = 0
    # for i in range(len(numbers_list)):
    #     res = done_queue.get()
    #     count += 1
    # for i in range(os.cpu_count()):
    #     task_queue.put('STOP')
    # all_time = time.perf_counter() - t_start
    # print(f"Success! Processed {count} numbers using Process and Queue in {all_time} seconds.\n")
    # results["multiprocessing_Process_Queue"] = all_time
    #
    # return results
    print("-" * 24)
    print("Generating numbers...")
    numbers_list = generate_data(count)
    print(f"Success! Generated {len(numbers_list)} numbers.", "\n--")
    results = {"count": count}

    print("Starting processing using single thread...")
    t_start = time.perf_counter()
    results_st = run_single_thread(numbers_list)
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_st)} numbers using single thread in {all_time} seconds.", "\n--")
    results["Single Thread"] = all_time

    print("Starting processing using ThreadPoolExecutor...")
    t_start = time.perf_counter()
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        results_tpe = list(executor.map(process_number, numbers_list))
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_tpe)} numbers using TPE in {all_time} seconds.", "\n--")
    results["ThreadPoolExecutor"] = all_time

    print("Starting processing using multiprocessing.Pool...")
    t_start = time.perf_counter()
    with Pool(os.cpu_count()) as pool:
        results_mppool = list(pool.map(process_number, numbers_list))
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_mppool)} numbers using mp.Pool in {all_time} seconds.", "\n--")
    results["multiprocessing_Pool"] = all_time

    task_queue = Queue()
    done_queue = Queue()
    for number in numbers_list:
        task_queue.put(number)
    print("Starting processing using Process and Queue...")
    t_start = time.perf_counter()
    for i in range(os.cpu_count()):
        Process(target=worker, args=(task_queue, done_queue)).start()
    count = 0
    for i in range(len(numbers_list)):
        res = done_queue.get()
        count += 1
    for i in range(os.cpu_count()):
        task_queue.put('STOP')
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {count} numbers using Process and Queue in {all_time} seconds.", "\n--")
    results["multiprocessing_Process_Queue"] = all_time

    return results


if __name__ == "__main__":
    test_perf(100000)
