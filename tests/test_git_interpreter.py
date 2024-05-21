import sys

sys.path.append("src")
import json
from rich import print
from git_interpreter import GitInterpreter

interpreter = GitInterpreter("tests/test_result.json", verbose=True)
result = interpreter.interpret_commits()
print(result)
