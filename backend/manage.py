#!/usr/bin/env python
import os, sys
from pathlib import Path

# Add parent directory to Python path so backend module can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
