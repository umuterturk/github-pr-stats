import csv
from typing import List


class CsvWriter:
    def __init__(
            self, file_name_prefix: str, raw_data_field_names: List[str], stats_field_names: List[str]
    ):
        self.raw_data_file_name = f"{file_name_prefix}_raw_data.csv" if file_name_prefix else None
        self.stats_file_name = f"{file_name_prefix}_stats.csv" if file_name_prefix else None
        self.raw_data_field_names = raw_data_field_names
        self.stats_field_names = stats_field_names

    def write_to_csv(self, file_name, data, mode='a', header=False):
        if not file_name:
            return
        with open(file_name, mode=mode, newline='') as csv_file:
            writer = csv.DictWriter(
                csv_file, fieldnames=self.raw_data_field_names if 'raw' in file_name else
                self.stats_field_names
            )
            if header:
                writer.writeheader()
            if isinstance(data, list):
                writer.writerows(data)
            elif data is not None:
                writer.writerow(data)

    def write_stats_header_to_csv(self):
        self.write_to_csv(self.stats_file_name, None, mode='w', header=True)

    def write_raw_data_header_to_csv(self):
        self.write_to_csv(self.raw_data_file_name, None, mode='w', header=True)
