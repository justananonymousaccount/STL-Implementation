# -*- coding: utf-8 -*-
import json
import argparse
import os
import sys

def count_entries(file_path):
    """
    Count entries in a JSON or JSONL file.
    - For .jsonl/.ndjson: each line is one entry.
    - For .json: if top-level is list or dict, count elements or keys.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jsonl', '.ndjson']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            raise
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data)
        else:
            raise ValueError(f"Unsupported JSON type {type(data)}; cannot count entries.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count entries in a JSON or JSONL file.')
    parser.add_argument('--file', help='Path to the .json or .jsonl file')
    parser.add_argument('--quiet', action='store_true', help='Only print the count, no extra text')
    args = parser.parse_args()

    try:
        total = count_entries(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.quiet:
        print(total)
    else:
        print(f"File '{args.file}' contains {total} entr{ 'y' if total == 1 else 'ies' }.")


