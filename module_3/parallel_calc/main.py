import math
import random
import os
import time
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


if __name__ == "__main__":
    print("Generating numbers...")
    numbers_list = generate_data(1000000)
    print(f"Success! Generated {len(numbers_list)} numbers.\n")

    print("Starting processing using single thread...")
    t_start = time.perf_counter()
    results_st = []
    for number in numbers_list:
        results_st.append(process_number(number))
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_st)} numbers using single thread in {all_time} seconds.\n")

    print("Starting processing using ThreadPoolExecutor...")
    t_start = time.perf_counter()
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        results_tpe = list(executor.map(process_number, numbers_list))
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_tpe)} numbers using TPE in {all_time} seconds.\n")

    print("Starting processing using multiprocessing.Pool...")
    t_start = time.perf_counter()
    with Pool(os.cpu_count()) as pool:
        results_mppool = list(pool.map(process_number, numbers_list))
    all_time = time.perf_counter() - t_start
    print(f"Success! Processed {len(results_mppool)} numbers using mp.Pool in {all_time} seconds.\n")

    print("Starting processing using Process and Queue...")
    # t_start = time.perf_counter()
    # queue = Queue()

