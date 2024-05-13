import sys

sys.path.append('src')
from git_extractor import GitExtractor

(
    GitExtractor(True).extract_commit_data(
        'C:/Users/gquintanar/Downloads/Repos/quantum-ip-video-jobs',
        'tests/test_result.json'
    )
)
