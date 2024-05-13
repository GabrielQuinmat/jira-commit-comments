from git import Repo, Commit, Diff
import pendulum as pdl
import logging
from rich.logging import RichHandler
import json


class GitExtractor:
    def __init__(self, verbose) -> None:
        FORMAT = '%(message)s'
        if verbose:
            logging.basicConfig(
                level='DEBUG', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        else:
            logging.basicConfig(
                level='INFO', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        self.log = logging.getLogger('rich')

    def get_user_commits(self, repo: Repo, user_email: str, date: pdl.DateTime):
        if not user_email:
            user_email = repo.config_reader().get_value('user', 'email')
        if not date:
            date = pdl.now()

        commits = []
        for branch in repo.branches:
            for commit in repo.iter_commits(
                branch,
                author=user_email,
                since=date.start_of('day'),
                until=date.end_of('day'),
            ):
                commits.append(commit)

        return commits

    def extract_commit_details(self, commit: Commit):
        timestamp = pdl.from_timestamp(commit.committed_date).format('YYYY-MM-DD HH:mm')
        author = commit.author.email
        comment = commit.message.strip()

        diff_details = []
        for diff in commit.parents[0].diff(commit, create_patch=True) if commit.parents else None:
            diff_details.append(self.extract_diff_details(diff))
        for index, diff in enumerate(commit.parents[0].diff(commit)) if commit.parents else None:
            diff_details[index]['change_type'] = self.extract_diff_details(diff)['change_type']

        return {
            'timestamp': timestamp,
            'author': author,
            'comment': comment,
            'diff_details': diff_details,
        }

    def extract_diff_details(self, diff: Diff):
        return {
            'change_type': diff.change_type,
            'a_path': diff.a_path,
            'b_path': diff.b_path,
            'diff': diff.diff.decode('utf-8') if diff.diff else '',
        }

    def extract_commit_data(
        self, repo_path: str, result_path: str, user_email: str = None, date: str = None
    ):
        repo = Repo(repo_path)

        commits = self.get_user_commits(repo, user_email, date)

        commit_details = []
        for commit in commits:
            details = self.extract_commit_details(commit)
            commit_details.append(details)

        commit_dict = []
        for details in commit_details:
            self.log.debug(f"Timestamp: {details['timestamp']}")
            self.log.debug(f"Author: {details['author']}")
            self.log.debug(f"Comment: {details['comment']}")
            self.log.debug(f'Diff Details:')
            for diff in details['diff_details']:
                self.log.debug(f"Change Type: {diff['change_type']}")
                self.log.debug(f"Old Path: {diff['a_path']}")
                self.log.debug(f"New Path: {diff['b_path']}")
                self.log.debug(f"Diff:\n{diff['diff']}")
            commit_dict.append(details)
        self.export_commit_data(result_path, commit_dict)

    def export_commit_data(self, result_path, commit_dict):
        """Export commit data to a JSON file."""
        with open(result_path, 'w') as file:
            json.dump(commit_dict, file, indent=4)
