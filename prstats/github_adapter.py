import requests

class GitHubAdapter:
    def __init__(self, token, start_date_iso):
        self.headers = {
            'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.start_date_iso = start_date_iso

    def fetch_data(self, url: str):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pull_requests(self, owner: str, repo: str):
        url = (f"https://api.github.com/repos/{owner}/"
               f"{repo}/pulls?state=closed&per_page=100&since={self.start_date_iso}")
        return self.fetch_data(url)

    def get_reviews(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self.fetch_data(url)

    def get_pr_timeline(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/timeline"
        return self.fetch_data(url)
