from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class PRStats:
    repository: str
    average_hours: float
    median_hours: float
    std_dev_hours: float
    p90_hours: float
    number_of_prs: int
    number_of_distinct_creators: int
    number_of_distinct_approvers: int
    number_of_distinct_users: int

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        def shorten_float(value):
            return round(value, 2) if isinstance(value, float) else value
        return {
            'repository': self.repository,
            'average_hours': shorten_float(self.average_hours),
            'median_hours': shorten_float(self.median_hours),
            'std_dev_hours': shorten_float(self.std_dev_hours),
            'p90_hours': shorten_float(self.p90_hours), 'number_of_prs': self.number_of_prs,
            'number_of_distinct_creators': self.number_of_distinct_creators,
            'number_of_distinct_approvers': self.number_of_distinct_approvers,
            'number_of_distinct_users': self.number_of_distinct_users
        }


@dataclass
class RawPRData:
    repository: str
    pr_number: int
    creator: str
    approver: str
    created_at: str
    closed_at: str
    approval_time_hours: float
    closing_time_hours: float

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {
            'repository': self.repository, 'pr_number': self.pr_number, 'creator': self.creator,
            'approver': self.approver, 'created_at': self.created_at, 'closed_at': self.closed_at,
            'approval_time_hours': self.approval_time_hours,
            'closing_time_hours': self.closing_time_hours
        }
