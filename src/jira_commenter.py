
from atlassian import Jira
from dotenv import load_dotenv
import os

load_dotenv()

class JiraCommen:
    def __init__(self) -> None:
        self.jira = Jira(
            url='https://jira.charter.com',
            token=os.getenv("JIRA_API_TOKEN")
        )

    
    def comment_issue(self, issue_key, comment):
        self.jira.issue_add_comment(issue_key, comment)
