import sys

sys.path.append('src')
from git_extractor import GitExtractor

(
    GitExtractor(True).extract_commit_data(
        'C:/Users/gquin/Downloads/Repos/jira-commit-comments',
        'tests/test_result.json',
        user_email="C-Gabriel.Quintanar@charter.com",
        before_date="2024-05-18",
        after_date="2024-05-01"
    )
)
