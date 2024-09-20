import hashlib
from datetime import datetime
from random import randint
from typing import List

from tabulate import tabulate

from prstats.csv_writer import CsvWriter
from prstats.github_adapter import GitHubAdapter
from prstats.pr_data_processor import PrDataProcessor

obfuscating_salt = str(randint(0, 1000000))


class PrStatsGenerator:
    def __init__(
            self, repos: List[str], csv_writer: CsvWriter, github_adapter: GitHubAdapter,
            pr_data_processor: PrDataProcessor, start_date
    ):
        self.github_adapter = github_adapter
        self.pr_data_processor = pr_data_processor
        self.repos = repos
        self.csv_writer = csv_writer
        self.start_date = start_date

    def calculate_approval_time_stats_per_repo(self):
        self.csv_writer.write_stats_header_to_csv()
        self.csv_writer.write_raw_data_header_to_csv()

        all_repo_stats = []

        for repo in self.repos:
            try:
                owner, repo_name = repo.split('/')
                print(f"Calculating statistics for repository: {repo_name}")

                approval_times, pr_count, creators, approvers, raw_pr_data = (
                    self._gather_approval_times(
                    owner, repo_name
                ))
                self.csv_writer.write_to_csv(
                    self.csv_writer.raw_data_file_name, self._obfuscate_raw_data(raw_pr_data)
                )

                stats = self.pr_data_processor.calculate_statistics(
                    repo_name, approval_times, creators, approvers
                )
                if stats:
                    self.csv_writer.write_to_csv(self.csv_writer.stats_file_name, stats)
                    all_repo_stats.append(stats)
                else:
                    all_repo_stats.append(self._empty_stats(repo_name, pr_count))

                print(tabulate(all_repo_stats, headers="keys"))

            except Exception as e:
                print(f"Failed to calculate stats for {repo}: {e}")

        return all_repo_stats

    def _gather_approval_times(self, owner, repo_name):
        approval_times, closing_times, creators, approvers, raw_pr_data = [], [], [], [], []
        pull_requests = self.github_adapter.get_pull_requests(owner, repo_name)

        for pr in pull_requests:
            approval_time, closing_time, approver = self._get_approval_time(owner, repo_name, pr)
            if approval_time is not None:
                approval_times.append(approval_time)
                closing_times.append(closing_time)
                creators.append(pr['user']['login'])
                if approver:
                    approvers.append(approver)
                raw_pr_data.append(
                    self._prepare_raw_data(pr, approval_time, closing_time, repo_name, approver)
                )

        return approval_times, len(pull_requests), creators, approvers, raw_pr_data

    def _get_approval_time(self, owner, repo_name, pr):
        if pr['user']['login'].endswith('[bot]'):
            return None, None, None

        created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        if created_at < self.start_date:
            return None, None, None

        if pr.get('draft'):
            timeline = self.github_adapter.get_pr_timeline(owner, repo_name, pr['number'])
            created_at = self._get_ready_for_review_time(timeline) or created_at

        reviews = self.github_adapter.get_reviews(owner, repo_name, pr['number'])
        approved_at, approver = self._get_first_approval(reviews)

        approval_duration = (approved_at - created_at).total_seconds() if approved_at else None
        closing_duration = (datetime.strptime(
            pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ'
        ) - created_at).total_seconds()

        return approval_duration, closing_duration, approver

    @staticmethod
    def _get_ready_for_review_time(timeline):
        for event in timeline:
            if event['event'] == 'ready_for_review':
                return datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        return None

    @staticmethod
    def _get_first_approval(reviews):
        for review in reviews:
            if review['state'] == 'APPROVED':
                approved_at = datetime.strptime(review['submitted_at'], '%Y-%m-%dT%H:%M:%SZ')
                return approved_at, review['user']['login']
        return None, None

    def _prepare_raw_data(self, pr, approval_time, closing_time, repo_name, approver):
        return {
            'repository': repo_name, 'pr_number': pr['number'], 'creator': pr['user']['login'],
            'approver': approver, 'created_at': pr['created_at'], 'closed_at': pr['closed_at'],
            'approval_time_hours': approval_time / 3600 if approval_time else 'N/A',
            'closing_time_hours': closing_time / 3600 if closing_time else 'N/A'
        }

    @staticmethod
    def obfuscate(s: str):
        return hashlib.md5(
            (hashlib.md5(s.encode()).hexdigest() + obfuscating_salt).encode()
        ).hexdigest()[:10] if s else None

    def _obfuscate_raw_data(self, raw_pr_data):
        for pr_data in raw_pr_data:
            pr_data['creator'] = self.obfuscate(pr_data['creator'])
            pr_data['approver'] = self.obfuscate(pr_data['approver'])
        return raw_pr_data

    @staticmethod
    def _empty_stats(repo_name, pr_count):
        return {
            'repository': repo_name, 'average_hours': 'N/A', 'median_hours': 'N/A',
            'std_dev_hours': 'N/A', 'p90_hours': 'N/A', 'number_of_prs': pr_count,
            'number_of_distinct_creators': 0, 'number_of_distinct_approvers': 0,
            'number_of_distinct_users': 0
        }
