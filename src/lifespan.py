import psutil
import threading
import datetime
from json import dumps

from loguru import logger
from fastapi import FastAPI


from src.stress import (
    cpu_stress,
    terminate_all_processes,
    allocate_mem_ram
    )


PERCENT_RAM = 0
PERCENT_CPU = 0
HEALTH_STATUS = {
    "status": "200 OK"
}


def monitor_health():
    while True:

        cpu_usage = psutil.cpu_percent(interval=1)
        core_usage = psutil.cpu_percent(percpu=True)
        memory_usage = psutil.virtual_memory().percent

        core_usage_dict = {}
        for index, usage in enumerate(core_usage):
            core_usage_dict[f"Cernel {index}"] = f"{usage}%"

        HEALTH_STATUS['cpu core usage'] = core_usage_dict
        HEALTH_STATUS['cpu usage'] = f'{cpu_usage:.2f} %'
        HEALTH_STATUS['memory usage'] = f'{memory_usage:.2f} %'
        HEALTH_STATUS['datetime_utc'] = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        logger.trace(
            dumps(
                HEALTH_STATUS,
                ensure_ascii=False,
                indent=4
                )
            )
        threading.Event().wait(2)


async def lifespan(app: FastAPI):
    ################## Startup here ######################
    threading.Thread(target=monitor_health, daemon=True).start()

    processes = cpu_stress(PERCENT_CPU)
    allocated_ram = allocate_mem_ram(PERCENT_RAM)

    yield
    ##################### Endup here ######################

    terminate_all_processes(processes)
    del allocated_ram
