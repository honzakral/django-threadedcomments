#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.test.simple import run_tests

if __name__ == "__main__":
    failures = run_tests(['threadedcomments', 'comments'], verbosity=9)
    if failures:
        sys.exit(failures)
