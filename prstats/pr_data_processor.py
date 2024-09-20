import statistics
from typing import List

import numpy as np


class PrDataProcessor:
    @staticmethod
    def filter_outliers(data: List[float]):
        if not data:
            return data

        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return [x for x in data if lower_bound <= x <= upper_bound]

    def calculate_statistics(self, repo, approval_times, creators, approvers):
        filtered_times = self.filter_outliers(approval_times)
        if not filtered_times:
            return None

        return {
            'repository': repo, 'average_hours': statistics.mean(filtered_times) / 3600,
            'median_hours': statistics.median(filtered_times) / 3600,
            'std_dev_hours': (statistics.stdev(
                filtered_times
            ) if len(
                filtered_times
            ) > 1 else 0) / 3600, 'p90_hours': np.percentile(filtered_times, 90) / 3600,
            'number_of_prs': len(approval_times), 'number_of_distinct_creators': len(set(creators)),
            'number_of_distinct_approvers': len(set(approvers)),
            'number_of_distinct_users': len(set(creators).union(set(approvers))),
        }
