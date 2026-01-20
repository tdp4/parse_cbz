#!/usr/bin/env python3
"""
Demo script showing how to use the CBZ parser with the cbz_files.txt file.
"""

from cbz_parser import parse_cbz_filename
from pathlib import Path


def main():
    # Read the file list
    cbz_list_file = Path("cbz_files.txt")
    
    if not cbz_list_file.exists():
        print(f"Error: {cbz_list_file} not found")
        return
    
    with open(cbz_list_file, 'r', encoding='utf-8') as f:
        filenames = f.readlines()
    
    print(f"Loaded {len(filenames)} filenames\n")
    
    # Parse all files
    cbz_files = []
    for filename in filenames[:20]:  # Demo with first 20 files
        filename = filename.strip()
        if filename:
            cbz = parse_cbz_filename(filename)
            cbz_files.append(cbz)
    
    # Example 1: Show parsed data for first 10 files
    print("=" * 80)
    print("Example 1: First 10 Parsed Files")
    print("=" * 80)
    for cbz in cbz_files[:10]:
        print(f"\n{cbz.display_name}")
        print(f"  Title: {cbz.title}")
        if cbz.chapter:
            print(f"  Chapter: {cbz.chapter}")
        if cbz.volume:
            print(f"  Volume: {cbz.volume}")
        if cbz.year:
            print(f"  Year: {cbz.year}")
        if cbz.uploader:
            print(f"  Uploader: {cbz.uploader}")
    
    # Example 2: Group by title
    print("\n" + "=" * 80)
    print("Example 2: Files Grouped by Title")
    print("=" * 80)
    
    by_title = {}
    for cbz in cbz_files:
        if cbz.title not in by_title:
            by_title[cbz.title] = []
        by_title[cbz.title].append(cbz)
    
    for title, files in sorted(by_title.items()):
        print(f"\n{title}: {len(files)} file(s)")
        for cbz in sorted(files, key=lambda x: x.sort_key):
            print(f"  - {cbz.display_name}")
    
    # Example 3: Filter by year
    print("\n" + "=" * 80)
    print("Example 3: Files from 2025")
    print("=" * 80)
    
    files_2025 = [cbz for cbz in cbz_files if cbz.year == 2025]
    for cbz in files_2025[:5]:  # Show first 5
        print(f"  - {cbz.display_name}")
    print(f"\nTotal 2025 files in this sample: {len(files_2025)}")
    
    # Example 4: Accessing specific properties
    print("\n" + "=" * 80)
    print("Example 4: Using Properties and Methods")
    print("=" * 80)
    
    sample = cbz_files[0]
    print(f"\nSample file: {sample.raw_filename}")
    print(f"  Display name: {sample.display_name}")
    print(f"  Chapter number (float): {sample.chapter_number}")
    print(f"  Volume number (int): {sample.volume_number}")
    print(f"  Sort key: {sample.sort_key}")
    print(f"  Is digital: {sample.is_digital}")
    print(f"  Is one-shot: {sample.is_oneshot}")


if __name__ == "__main__":
    main()
