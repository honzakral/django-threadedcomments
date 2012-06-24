import sys
sys.path.append('..')

import os
# Make a backup of DJANGO_SETTINGS_MODULE environment variable to restore later.
backup = os.environ.get('DJANGO_SETTINGS_MODULE', '')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.test.simple import DjangoTestSuiteRunner

if __name__ == "__main__":
    runner = DjangoTestSuiteRunner(verbosity=9)
    failures = runner.run_tests(['threadedcomments',])
    if failures:
        sys.exit(failures)
    # Reset the DJANGO_SETTINGS_MODULE to what it was before running tests.
    os.environ['DJANGO_SETTINGS_MODULE'] = backup
