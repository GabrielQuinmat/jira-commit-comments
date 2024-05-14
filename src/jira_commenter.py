from atlassian import Jira
from dotenv import load_dotenv

load_dotenv()


class JiraCommen:
    def __init__(self) -> None:
        oauth2_dict = {
            "client_id": os.getenv("JIRA_CLIENT_ID"),
            "token": os.getenv("JIRA_API_TOKEN"),
        }
        self.jira = Jira(
            url=os.getenv("JIRA_URL"),
            cloud=True,
            oauth2=oauth2_dict,
        )
    
    def comment_issue(self, issue_key, comment):
        self.jira.issue_add_comment(issue_key, comment)
