import threading
import time
import timeit
import multiprocessing as mp

repetitions = 50000

def thread_function(r : range, store_list = None):
    data = [0] * len(r)
    global repetitions
    for _ in range(repetitions):
        for i in range(len(data)):
            data[i] = i
    if store_list is not None:
        store_list.append((data, r))
    else:
        return data


def do_multi(l, store_list):
    r1 = range(int(l/2))
    r2 = range(r1.stop, l)
    th1 = mp.Process(target=thread_function, args=(r1, store_list))
    th2 = mp.Process(target=thread_function, args=(r2, store_list))
    th1.start()
    th2.start()
    th1.join()
    th2.join()


if __name__ == "__main__":
    manager = mp.Manager()
    m_list = manager.list()

    t0 = time.time()
    buffer = thread_function(range(repetitions))
    t1 = time.time()
    print(f'Done in {t1-t0}')
    t0 = time.time()
    do_multi(repetitions, m_list)
    t1 = time.time()
    print(f'Done in {t1-t0}')
