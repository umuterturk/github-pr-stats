import concurrent.futures
import hashlib
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from random import randint
from typing import List, Tuple, Dict, Optional

from tabulate import tabulate

from prstats.csv_writer import CsvWriter
from prstats.github_adapter import GitHubAdapter
from prstats.models import RawPRData
from prstats.pr_data_processor import PrDataProcessor
from prstats.safe_print import safe_print, OperationTable


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
        self.obfuscating_salt = str(randint(0, 1000000))
        self.operation_table = OperationTable(repos)

    def calculate_stats_for_repo(self, repo):
        try:
            owner, repo_name = repo.split('/')
            # safe_print(f"Calculating statistics for repository: {repo_name}")
            self.operation_table.start_operation(repo)

            approval_times, pr_count, creators, raw_pr_data = (
                self._gather_approval_times(owner, repo_name))
            self.csv_writer.write_raw_data(raw_pr_data)

            stats = self.pr_data_processor.calculate_statistics(
                repo_name, approval_times, creators
            )
            self.operation_table.complete_operation(repo)
            if stats:
                self.csv_writer.write_stats(stats)
                safe_print(f"Finished for {repo_name}")
                return stats.to_dict()
            else:
                return self._empty_stats(repo_name, pr_count)

        except Exception as e:
            # print stack trace with tracer
            exception_trace = traceback.format_exc()
            safe_print(exception_trace)
            safe_print(f"Failed to calculate stats for {repo}: {e}")
            self.operation_table.handle_error(repo, e.__class__.__name__)
            return None

    def calculate_approval_time_stats_per_repo(self):
        self.csv_writer.write_stats_header()
        self.csv_writer.write_raw_data_header()

        all_repo_stats = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_repo = {executor.submit(self.calculate_stats_for_repo, repo): repo for repo in
                              self.repos}
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    data = future.result()
                    if data:
                        all_repo_stats.append(data)
                except Exception as e:
                    safe_print(f"Failed to calculate stats for {repo}: {e}")

        safe_print(tabulate(all_repo_stats, headers="keys"))
        return all_repo_stats

    def _gather_approval_times(self, owner, repo_name) -> Tuple[
        List[int], int, List[str], List[RawPRData]]:
        merge_times, closing_times, creators, raw_pr_data = [], [], [], []
        pull_requests = self.github_adapter.get_pull_requests(owner, repo_name)

        def process_pr(pr):
            merge_time, closing_time = self._get_approval_time(owner, repo_name, pr)
            if merge_time is not None:
                return merge_time, closing_time, pr['user']['login'], self._prepare_raw_data(
                    pr, merge_time, closing_time, repo_name
                )
            return None

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_pr, pr): pr for pr in pull_requests}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    approval_time, closing_time, creator, raw_data = result
                    merge_times.append(approval_time)
                    closing_times.append(closing_time)
                    creators.append(creator)

                    raw_pr_data.append(raw_data)

        return merge_times, len(pull_requests), creators, raw_pr_data

    def _get_approval_time(self, owner, repo_name, pr):
        if pr['user']['login'].endswith('[bot]'):
            return None, None

        created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        if created_at < self.start_date:
            return None, None

        if pr.get('draft'):
            timeline = self.github_adapter.get_pr_timeline(owner, repo_name, pr['number'])
            created_at = self._get_ready_for_review_time(timeline) or created_at

        # reviews = self.github_adapter.get_reviews(owner, repo_name, pr['number'])
        # approved_at, approver = self._get_first_approval(reviews)
        approved_at = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
        approval_duration = (approved_at - created_at).total_seconds() if approved_at else None
        closing_duration = (datetime.strptime(
            pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ'
        ) - created_at).total_seconds()

        return approval_duration, closing_duration

    @staticmethod
    def _get_ready_for_review_time(timeline):
        for event in timeline[0]:
            try:
                if event['event'] == 'ready_for_review':
                    return datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            except Exception as e:
                safe_print(f"Failed to get ready for review time: {e}")
        return None

    @staticmethod
    def _get_first_approval(reviews):
        for review in reviews[0]:
            try:
                if review['state'] == 'APPROVED':
                    approved_at = datetime.strptime(review['submitted_at'], '%Y-%m-%dT%H:%M:%SZ')
                    return approved_at, review['user']['login']
            except Exception as e:
                safe_print(f"Failed to get approval time: {e}")

        return None, None

    def _prepare_raw_data(
            self, pr: Dict, approval_time: Optional[float], closing_time: Optional[float],
            repo_name: str
            ) -> RawPRData:
        return RawPRData(
            repository=repo_name, pr_number=pr['number'],
            creator=self.obfuscate(pr['user']['login']), created_at=pr['created_at'],
            closed_at=pr['closed_at'],
            merge_time_hours=approval_time / 3600 if approval_time else 'N/A',
            closing_time_hours=closing_time / 3600 if closing_time else 'N/A'
        )

    def obfuscate(self, s: str):
        return hashlib.md5(
            (hashlib.md5(s.encode()).hexdigest() + self.obfuscating_salt).encode()
        ).hexdigest()[:10] if s else None

    @staticmethod
    def _empty_stats(repo_name, pr_count):
        return {
            'repository': repo_name, 'average_hours': 'N/A', 'median_hours': 'N/A',
            'std_dev_hours': 'N/A', 'p90_hours': 'N/A', 'number_of_prs': pr_count,
            'number_of_distinct_creators': 0
        }
