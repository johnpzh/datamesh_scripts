import sys
import time
import argparse
from datetime import datetime

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver


import networkx as nx
import pandas as pd
import os
import glob


class EventMonitor(FileSystemEventHandler):

    def __init__(self):
        pass

    def _filter_event(self, event) -> bool:
        if event.src_path.endswith(("_r_stat", "_w_stat")) and \
            event.event_type == "created" and \
            event.is_directory == False:
            return True
        else:
            return False


    def on_any_event(self, event: FileSystemEvent) -> None:
        if self._filter_event(event):
            # print(f"\n+++ time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, valid_event: {event}")
            print(f"\n+++ {event}")
        else:
            # print(f"\n--- time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, invalid_event: {event}")
            print(f"\n--- {event}")
            pass  # Do nothing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", type=str, help="Directory to monitor for events")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(-1)

    dest_path = args.input_directory

    event_monitor = EventMonitor()
    # observer = Observer()
    observer = PollingObserver()
    observer.schedule(event_monitor, dest_path, recursive=True)
    observer.start()
    print(f"Monitoring directory: {dest_path}")
    try:
        start_time = time.time()
        while True:
            print(".", end='', flush=True)  # Heartbeat
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()