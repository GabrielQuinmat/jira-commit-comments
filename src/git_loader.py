from typing import AsyncIterator, Iterator
import json
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class GitDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """
        with open(self.file_path, encoding="utf-8") as f:
            json_data = json.load(f)
            for branch, commits in json_data.items():
                line_number = 0
                for commit in commits:
                    line = (
                        f'Timestamp: {commit["timestamp"]}\n'
                        f'Comment: {commit["comment"]}\n'
                        'Diffs:\n'
                    )
                    for diff in commit["diff_details"]:
                        line += f"Change Type: {diff['change_type']}\n"
                        line += f"Diff:\n{diff['diff']}\n"
                    yield Document(
                        page_content=line,
                        metadata={
                            "source": self.file_path,
                            "line_number": line_number,
                            "branch": branch,
                        },
                    )
                    line_number += 1

    # alazy_load is OPTIONAL.
    # If you leave out the implementation, a default implementation which delegates to lazy_load will be used!
    async def alazy_load(
        self,
    ) -> AsyncIterator[Document]:  # <-- Does not take any arguments
        """An async lazy loader that reads a file line by line."""
        # Requires aiofiles
        # Install with `pip install aiofiles`
        # https://github.com/Tinche/aiofiles
        import aiofiles

        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            json_data = json.load(f)
            line_number = 0
            async for branch, commits in json_data.items():
                for commit in commits:
                    line = (
                        f"Timestamp: {commit.timestamp}\n"
                        f"Comment: {commit.comment}\n"
                    )
                    for diff in commit["diff_details"]:
                        line += f"Change Type: {diff['change_type']}\n"
                        line += f"Diff:\n{diff['diff']}\n"
                    yield Document(
                        page_content=line,
                        metadata={
                            "source": self.file_path,
                            "line_number": line_number,
                            "branch": commit["branch"],
                        },
                    )
                    line_number += 1
