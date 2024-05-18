import sys

sys.path.append('src')
import typer
import os
from rich.progress import Progress, SpinnerColumn, TextColumn
import tempfile


app = typer.Typer()


@app.command()
def main(
    repo: str, json_path: str, user_email=None, date=None, verbose: bool = False
):
    from git_extractor import GitExtractor
    from git_interpreter import GitInterpreter

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        transient=True,
    ) as progress:
        progress.add_task('[green]Extracting commit data...', total=1)
        # GitExtractor(verbose).extract_commit_data(
        #     repo, json_path, user_email=user_email, date=date
        # )
        progress.update(task_id=0, completed=1)
        progress.add_task('[green]Interpreting commit data...', total=1)
        # comment = GitInterpreter(verbose, json_path).interpret_commits()
        # if comment == -1:
        #     typer.echo("No commits found. Aborting...")
        #     return
        comment = 'This is a comment. Jira tickets are important.'
        progress.update(task_id=1, completed=1)
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(comment)
        temp_file_path = temp_file.name
    typer.launch(temp_file_path, wait=True)
    with open(temp_file_path, "r") as file:
        edited_text = file.read()
    os.unlink(temp_file_path)
    typer.echo(f"Final Comment: {edited_text}")




if __name__ == '__main__':
    app()
