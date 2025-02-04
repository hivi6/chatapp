import os
import unittest

if __name__ == "__main__":
    start_dir = os.environ.get("TESTDIR", "backend/tests")

    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=start_dir, pattern="test_*.py")

    test_runner = unittest.TextTestRunner(verbosity=3)
    test_runner.run(test_suite)
