import requests

class GitHubAdapter:
    def __init__(self, token, start_date_iso):
        self.headers = {
            'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.start_date_iso = start_date_iso

    def _fetch_data(self, url: str):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json(), response.headers

    def get_pull_requests(self, owner: str, repo: str):
        url = (f"https://api.github.com/repos/{owner}/{repo}/pulls?"
               f"state=closed&per_page=100&sort=created&direction=desc&since={self.start_date_iso}")
        all_prs = []
        while url:
            data, headers = self._fetch_data(url)
            # filter out prs merged before the start date
            go_to_next_page = True
            for pr in data:
                if 'created_at' in pr and pr['created_at'] and pr['created_at'] < self.start_date_iso:
                    go_to_next_page = False
                    # break while loop
                    break
                else:
                    # if pr is created by a bot skip it
                    if not pr['user']['login'].endswith('[bot]') and 'merged_at' in pr and pr['merged_at']:
                        all_prs.append(pr)

            if not go_to_next_page:
                break

            # Check for the 'Link' header to see if there's a 'next' page
            if 'Link' in headers:
                links = self._parse_link_header(headers['Link'])
                url = links.get('next')  # Get the URL for the next page
            else:
                url = None  # No more pages left

        return all_prs

    def _parse_link_header(self, link_header: str):
        """Parses the Link header and returns a dictionary of rel -> URL."""
        links = {}
        for link in link_header.split(','):
            section = link.split(';')
            url = section[0].strip('<> ')
            name = section[1].strip().split('=')[1].strip('"')
            links[name] = url
        return links

    def get_reviews(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self._fetch_data(url)

    def get_pr_timeline(self, owner, repo, pr_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/timeline"
        return self._fetch_data(url)
