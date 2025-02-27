#!/usr/bin/env python3

import time
import sys
import os

from dispatcher.config import setup
from tests.data.methods import sleep_function  # or any existing @task to run

def main():
    if len(sys.argv) < 2:
        print("Usage: submit_many_tasks.py <CONFIG_FILE> [<NUM_TASKS>]")
        sys.exit(1)

    config_file = sys.argv[1]
    num_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 50  # default 50 tasks

    # Load the specified config
    setup(file_path=config_file)

    print(f"Submitting {num_tasks} tasks using config {config_file}...")

    for i in range(num_tasks):
        # Each worker will sleep 15s, creating enough concurrency to keep them busy
        sleep_function.apply_async(args=[15])
    print("Tasks submitted.")

if __name__ == "__main__":
    main()
