from git import Repo, Commit, Diff
import pendulum as pdl
import logging
from rich.logging import RichHandler
import json


class GitExtractor:
    def __init__(self, verbose) -> None:
        FORMAT = "%(message)s"
        if verbose:
            logging.basicConfig(
                level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
            )
        else:
            logging.basicConfig(
                level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
            )
        self.log = logging.getLogger("rich")

    def get_user_commits(
        self,
        repo: Repo,
        user_email: str,
        before_date: pdl.DateTime,
        after_date: pdl.DateTime,
    ):
        if not user_email:
            user_email = repo.config_reader().get_value("user", "email")
        if not before_date or not after_date:
            before_date = pdl.now()
            after_date = pdl.now()

        commit_dict = {}
        for branch in repo.branches:
            self.log.debug(f"Branch: {branch.name}")
            commits = []
            for commit in repo.iter_commits(
                branch,
                author=user_email,
                since=after_date.start_of("day"),
                until=before_date.end_of("day"),
            ):
                self.log.debug(f"Commit: {commit.committed_datetime}")
                commits.append(commit)
            commit_dict[branch.name] = commits

        return commit_dict

    def extract_commit_details(self, commit: Commit):
        timestamp = pdl.from_timestamp(commit.committed_date).format("YYYY-MM-DD HH:mm")
        author = commit.author.email
        comment = commit.message.strip()

        diff_details = []
        for diff in (
            commit.parents[0].diff(commit, create_patch=True) if commit.parents else []
        ):
            diff_details.append(self.extract_diff_details(diff))
        for index, diff in (
            enumerate(commit.parents[0].diff(commit)) if commit.parents else []
        ):
            diff_details[index]["change_type"] = self.extract_diff_details(diff)[
                "change_type"
            ]

        return {
            "timestamp": timestamp,
            "author": author,
            "comment": comment,
            "diff_details": diff_details,
        }

    def extract_diff_details(self, diff: Diff):
        return {
            "change_type": diff.change_type,
            "a_path": diff.a_path,
            "b_path": diff.b_path,
            "diff": diff.diff.decode("utf-8") if diff.diff else "",
        }

    def extract_commit_data(
        self,
        repo_path: str,
        result_path: str,
        user_email: str = None,
        before_date: str = None,
        after_date: str = None,
    ):
        repo = Repo(repo_path)
        self.log.debug(f"Extracting commit data from {repo}")

        commits_dict = self.get_user_commits(
            repo, user_email, pdl.parse(before_date), pdl.parse(after_date)
        )

        final_data = {}
        for branch, commits in commits_dict.items():
            branch_data = []
            commit_details = []
            for commit in commits:
                details = self.extract_commit_details(commit)
                commit_details.append(details)

            for details in commit_details:
                self.log.debug(f"Branch: {branch}")
                self.log.debug(f"Timestamp: {details['timestamp']}")
                self.log.debug(f"Author: {details['author']}")
                self.log.debug(f"Comment: {details['comment']}")
                self.log.debug(f"Diff Details:")
                for diff in details["diff_details"]:
                    self.log.debug(f"Change Type: {diff['change_type']}")
                    self.log.debug(f"Old Path: {diff['a_path']}")
                    self.log.debug(f"New Path: {diff['b_path']}")
                    self.log.debug(f"Diff:\n{diff['diff']}")
                branch_data.append(details)
            final_data[branch] = branch_data
        self.export_commit_data(result_path, final_data)

    def export_commit_data(self, result_path, commit_dict):
        """Export commit data to a JSON file."""
        with open(result_path, "w") as file:
            json.dump(commit_dict, file, indent=4)
