import sys

sys.path.append("src")
import json
from rich import print
from git_interpreter import GitInterpreter

interpreter = GitInterpreter(True, 'tests/test_result.json')
result = interpreter.interpret_commits()
print(result)