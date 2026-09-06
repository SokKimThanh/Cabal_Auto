import unittest
import sys

if __name__ == '__main__':
    loader = unittest.TestLoader()
    if len(sys.argv) > 1:
        # Load specific test module
        test_module = sys.argv[1].replace('/', '.').replace('\\', '.').replace('.py', '')
        suite = loader.loadTestsFromName(test_module)
    else:
        # Discover and run all tests
        suite = loader.discover('tests')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
