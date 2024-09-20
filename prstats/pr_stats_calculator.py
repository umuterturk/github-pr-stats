import argparse
from datetime import datetime, timedelta

from prstats.csv_writer import CsvWriter
from prstats.github_adapter import GitHubAdapter
from prstats.pr_data_processor import PrDataProcessor
from prstats.stats_generator import PrStatsGenerator


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some repositories.')
    parser.add_argument(
        'repos', metavar='R', type=str, nargs='+',
        help='a list of repositories in the format "owner/repo"'
    )
    parser.add_argument(
        '--token', metavar='T', type=str, required=True,
        help='GitHub token for authentication with read access to the repositories'
    )
    parser.add_argument(
        '--days', metavar='D', type=int, default=60,
        help='number of days to look back from today (default: 60)'
    )
    parser.add_argument(
        '--file', metavar='F', type=str, required=False, default='pr_approval_',
        help='File name prefix to save the raw data and stats'
    )
    return parser.parse_args()


args = parse_arguments()

REPOS = args.repos
GITHUB_TOKEN = args.token
days_to_look_back = args.days
file_name_prefix = args.file

today = datetime.utcnow()
start_date = today - timedelta(days=days_to_look_back)
start_date_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')

if __name__ == "__main__":
    raw_data_field_names = ['repository', 'pr_number', 'creator', 'approver', 'created_at',
                            'closed_at', 'approval_time_hours', 'closing_time_hours']
    stats_field_names = ['repository', 'average_hours', 'median_hours', 'std_dev_hours',
                         'p90_hours', 'number_of_prs', 'number_of_distinct_creators',
                         'number_of_distinct_approvers', 'number_of_distinct_users']

    csv_writer = CsvWriter(file_name_prefix, raw_data_field_names, stats_field_names)
    github_adapter = GitHubAdapter(GITHUB_TOKEN, start_date_iso)
    pr_data_processor = PrDataProcessor()
    pr_stats_calculator = PrStatsGenerator(REPOS, csv_writer, github_adapter, pr_data_processor, start_date)

    pr_stats_calculator.calculate_approval_time_stats_per_repo()
