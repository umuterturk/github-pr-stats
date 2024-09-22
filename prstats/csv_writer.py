import csv
import threading
from typing import List, Optional

from prstats.models import PRStats, RawPRData


class CsvWriter:
    def __init__(
            self, file_name_prefix: str
    ):
        self.raw_data_file_name = f"{file_name_prefix}_raw_data.csv" if file_name_prefix else None
        self.stats_file_name = f"{file_name_prefix}_stats.csv" if file_name_prefix else None
        self.lock = threading.Lock()  # Initialize the lock

    def write_stats_header(self):
        with self.lock:
            attribute_names = PRStats.__annotations__.keys()
            self._write_header(self.stats_file_name, attribute_names)

    def write_raw_data_header(self):
        with self.lock:
            attribute_names = RawPRData.__annotations__.keys()
            self._write_header(self.raw_data_file_name, attribute_names)

    def write_raw_data(self, raw_pr_data_list:List[RawPRData]):
        with self.lock:
            for raw_pr_data in raw_pr_data_list:
                self._write_data(self.raw_data_file_name, raw_pr_data.to_dict())

    def write_stats(self, stats:PRStats):
        with self.lock:
            self._write_data(self.stats_file_name, stats.to_dict())

    def _write_data(self, file_name:Optional[str], data:dict):
        if not file_name:
            return
        with open(file_name, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data.keys())
            writer.writerow(data)


    def _write_header(self, file_name:Optional[str], attribute_names:List[str]):
        if not file_name:
            return
        with open(file_name, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=attribute_names)
            writer.writeheader()
