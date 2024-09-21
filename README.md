# PR Approval Time Stats Calculator

## Overview

The **PR Approval Time Stats Calculator** is a Python tool designed to gather and analyze pull request (PR) data from specified GitHub repositories. The tool retrieves PRs that have been closed within a given timeframe, calculates approval times, and compiles various statistics related to the approval and closing of these PRs. The results are saved to CSV files, which can be used for further analysis.

This tool is particularly useful for teams and developers who want to gain insights into their code review processes, such as how long it takes for PRs to get approved and how these times vary across different repositories.

## Features

- Fetches closed pull requests from specified GitHub repositories.
- Calculates the time it takes for pull requests to be approved after they are opened.
- Filters out outliers from the data to provide more accurate statistics.
- Generates and saves both raw PR data and statistical summaries in CSV format.
- Obfuscates the usernames of PR creators and approvers to protect their privacy.

## Requirements

- Python 3.7+
- Required Python packages (install using `pip`):
  - `requests`
  - `numpy`
  - `tabulate`

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:umuterturk/github-pr-stats.git
   cd github-pr-stats
   ```

2. Setup venv and install the required Python packages:
   ```bash
   ./setup.sh
   source venv/bin/activate
   ```

## Github permissions
You need to create access token from https://github.com/settings/personal-access-tokens/new and give it `repo` read-only permission and select repositories you want to analyze. 

## Usage

To use the PR Approval Time Stats Calculator, run the script with the following command-line arguments:

```bash
python pr_stats_calculator.py [OPTIONS] REPOSITORIES
```

Or you can grab the executable from [releases](https://github.com/umuterturk/github-pr-stats/releases).

```bash
./pr_stats_calculator [OPTIONS] REPOSITORIES
```

### Required Arguments

- `REPOSITORIES`: A list of repositories to analyze in the format `owner/repo`. You can specify multiple repositories by separating them with spaces.

### Optional Arguments

- `--token` (`-T`): The GitHub token with read access to the repositories. This is required for authentication with the GitHub API.
- `--days` (`-D`): The number of days to look back from today to fetch PR data. Default is 60 days.
- `--file` (`-F`): The prefix for the CSV files where raw data and statistics will be saved. Default is `pr_approval_`.

### Example Usage

```bash
# writes to a file uses last 30 days data
python pr_stats_calculator.py --token YOUR_GITHUB_TOKEN --days 30 --file my_repo_stats owner1/repo1 owner2/repo2

# only prints, doesn't write to a file, uses 60 days data as it is not set
python pr_stats_calculator.py --token YOUR_GITHUB_TOKEN owner1/repo1 owner2/repo2
```

This command will:
- Fetch pull request data from `owner1/repo1` and `owner2/repo2`.
- Look back 30 days from today.
- Save the raw PR data in a file named `my_repo_stats_raw_data.csv`.
- Save the calculated statistics in a file named `my_repo_stats_stats.csv`.

### Output Files

- **Raw Data File** (`<file_name_prefix>_raw_data.csv`): Contains detailed information about each PR, including the obfuscated usernames of the creator and approver, the time taken for approval, and the time taken to close the PR.

- **Statistics File** (`<file_name_prefix>_stats.csv`): Contains summarized statistics, including the average, median, standard deviation, and 90th percentile of approval times, as well as counts of distinct creators and approvers.

### Notes

- The tool obfuscates the usernames of PR creators and approvers to protect privacy.
- Outliers in the approval times are filtered out before calculating the statistics to ensure more reliable insights.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or need further assistance, please feel free to reach out:

- **GitHub**: [umuterturk](https://github.com/umuterturk)

---

Thank you for using the PR Approval Time Stats Calculator! We hope this tool helps you gain valuable insights into your code review process.
