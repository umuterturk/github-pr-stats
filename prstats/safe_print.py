# use a lock to prevent multiple threads from writing to the same time
import os
import threading
from rich.console import Console
from rich.table import Table
import time

_lock = threading.Lock()
def safe_print(*args, **kwargs):
    pass
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_print("Cannot display this output")



class OperationTable:
    def __init__(self, operations):
        self.console = Console()
        self.operations = operations
        self.status_icons = {op: ":black_circle:" for op in operations}  # Initial status: not started
        self.start_times = {}
        self.time_spent = {op: None for op in operations}  # Time spent for each operation
        self.errors = {op: None for op in operations}  # Track errors for each operation
        self.table = Table()
        self.table.add_column("Repo", justify="center", style="cyan", no_wrap=True)
        self.table.add_column("Status", justify="center", style="magenta")
        self.table.add_column("Time Spent (s)", justify="center", style="green")
        self.table.add_column("Error", justify="center", style="red")  # Error column

    def display_table(self):
        with _lock:
            self.clear_console()
            self.table = Table(title="Operations Status")
            self.table.add_column("Operation", justify="center", style="cyan", no_wrap=True)
            self.table.add_column("Status", justify="center", style="magenta")
            self.table.add_column("Time Spent (s)", justify="center", style="green")
            self.table.add_column("Error", justify="center", style="red")

            for op in self.operations:
                time_spent = self.time_spent[op]
                time_spent_str = f"{time_spent:.2f}" if time_spent is not None else "N/A"
                error_msg = self.errors[op] if self.errors[op] is not None else "None"
                self.table.add_row(op, self.status_icons[op], time_spent_str, error_msg)

            self.console.print(self.table)

    def start_operation(self, operation):
        self.start_times[operation] = time.time()  # Record start time
        self.status_icons[operation] = ":hourglass:"  # Set to in-progress icon
        self.display_table()

    def complete_operation(self, operation):
        end_time = time.time()
        self.time_spent[operation] = end_time - self.start_times[operation]  # Calculate time spent
        self.status_icons[operation] = ":white_check_mark:"  # Set to completed icon
        self.display_table()

    def handle_error(self, operation, error_message):
        self.errors[operation] = error_message  # Store the error message
        self.status_icons[operation] = ":x:"  # Set to error icon
        self.display_table()

    def clear_console(self):
        os.system("cls" if os.name == "nt" else "clear")
