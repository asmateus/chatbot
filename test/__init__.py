import os
import sys

TEST_TARGET_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_TARGET_PATH += '/query/'


# Make test target visible to python
sys.path.insert(0, TEST_TARGET_PATH)
