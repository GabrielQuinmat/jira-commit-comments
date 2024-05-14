import typer
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()

@app.command()
def main(repo: str, json_path: str, verbose: bool = False):
    from git_extractor import GitExtractor
    from git_interpreter import GitInterpreter
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task("[green]Extracting commit data...", total=None)
        GitExtractor(verbose).extract_commit_data(repo, json_path)
        progress.update(task_id=0, completed=1)
        progress.add_task("[green]Interpreting commit data...", total=None)
        comment = GitInterpreter(verbose, json_path).interpret_commits()
        progress.update(task_id=1, completed=1)
        comment = Prompt.ask("Comment, edit if you want:", default=comment)


if __name__ == "__main__":
    app()