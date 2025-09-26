import multiprocessing
import random
import time
from functools import partial

import numpy as np

from main import GameProcess


def worker_process(seed, num_simulations):
    gp = GameProcess(seed)

    results = []
    for _ in range(num_simulations):
        result = gp.simulate(0)
        results.append(result)

    return np.array(results)


def main():
    num_processes = 10  # 并行进程数
    num_simulations = 100  # 每个进程的模拟次数

    pool = multiprocessing.Pool(processes=num_processes)

    seeds = [random.randint(0, 100000) for _ in range(num_processes)]  # 种子

    func = partial(worker_process, num_simulations=num_simulations)

    start_time = time.time()
    all_results = pool.map(func, seeds)
    pool.close()
    pool.join()

    print(f"\n时间 {time.time() - start_time:.2f}")
    res = np.concatenate(all_results)

    mean = np.mean(res[:, 0][res[:, 0] > -1])

    print(f"模拟次数: {len(res)}")
    print(f"平均值: {mean:.4f}")


if __name__ == '__main__':
    main()
