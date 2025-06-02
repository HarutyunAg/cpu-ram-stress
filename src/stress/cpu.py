import os
import psutil
from time import sleep
from loguru import logger
from multiprocessing import Process, Pipe



def _cpu_stress_test(conn, affinity=None, is_last_core=False, percent=100, check=False):
    proc = psutil.Process(os.getpid())
    cores_message = str(affinity[0]) if affinity else 'all'
    message = f"Process start: PID={proc.pid}, Core={cores_message}"
    logger.info(message)
    conn.send(message)
    conn.close()

    if affinity is not None:
        proc.cpu_affinity(affinity)

    while True:
        if not is_last_core or not check:
            _ = sum(i*i for i in range(1_000_000))
        elif is_last_core:
            last_core_idx = affinity[-1]
            load = psutil.cpu_percent(interval=0.1, percpu=True)[last_core_idx]
            
            if load > percent:
                sleep(0.1)
            else:
                _ = sum(i*i for i in range(1_000_000))     


def cpu_stress(cores, percent):
    procs = []
    conns = []

    for i in range(cores - 1):
        parent_conn, child_conn = Pipe()
        p = Process(
            target=_cpu_stress_test,
            kwargs={
            "conn": child_conn,
            "affinity": [i],
            "is_last_core": False,
            "percent": percent
            }
        )

        p.start()
        procs.append(p)
        conns.append(parent_conn)

    parent_conn, child_conn = Pipe()
    p = Process(target=_cpu_stress_test, kwargs=(child_conn, [cores - 1], True))
    p.start()
    procs.append(p)
    conns.append(parent_conn)
    return procs


def terminate_all_processes(processes: list[Process]):

    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join(timeout=0.05)
            if p.is_alive():
                p.kill()
                logger.warning(f"process {p.pid} was killed")
            else:
                logger.info(f"process {p.pid} was terminated")
