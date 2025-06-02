from psutil import virtual_memory
from ctypes import create_string_buffer

from loguru import logger


def allocate_mem_ram(percentage):

    if not (0 <= percentage <= 100):
        raise ValueError

    total_system_ram_bytes = virtual_memory().total
    total_system_ram_mb = total_system_ram_bytes // (1024 ** 2)
    ram_to_allocate_mb = int((total_system_ram_mb / 100) * percentage)
    logger.info(f'Allocate {ram_to_allocate_mb} mb of RAM')

    try:
        allocated_memory = create_string_buffer(ram_to_allocate_mb * 1024 * 1024)
        return allocated_memory
    except MemoryError as e:
        logger.error(e)
        return None
