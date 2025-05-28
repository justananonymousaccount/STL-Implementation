# -*- coding: utf-8 -*-
import json
import random
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Merge and shuffle multiple JSON array files into a single output file."
    )
    parser.add_argument(
        "--input_files", 
        required=True, 
        nargs="+", 
        help="Paths to the input JSON files (each should contain a JSON array)"
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Path for the merged and shuffled output JSON file"
    )
    
    args = parser.parse_args()

    merged_data = []
    # Iterate through each provided input file.
    for filepath in args.input_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged_data.extend(data)

    # Shuffle the merged list.
    random.shuffle(merged_data)

    # Write the shuffled list to the output file as a JSON array.
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)

    print(f"Merged and shuffled {len(merged_data)} entries into {args.output_file}")

if __name__ == "__main__":
    main()


