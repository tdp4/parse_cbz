#!/usr/bin/env python3
"""
Verify CBZ filename parsing across all files in cbz_files.txt
"""

from cbz_parser import parse_cbz_filename
from collections import defaultdict, Counter
from pathlib import Path


def main():
    # Read all filenames
    cbz_list_file = Path("cbz_files.txt")
    
    if not cbz_list_file.exists():
        print(f"Error: {cbz_list_file} not found")
        return
    
    with open(cbz_list_file, 'r', encoding='utf-8') as f:
        filenames = [line.strip() for line in f if line.strip()]
    
    print(f"Parsing {len(filenames)} files...")
    print("=" * 80)
    
    # Parse all files
    parsed_files = []
    issues = defaultdict(list)
    
    for filename in filenames:
        cbz = parse_cbz_filename(filename)
        parsed_files.append(cbz)
        
        # Check for potential issues
        if not cbz.title:
            issues['no_title'].append((filename, cbz))
        elif cbz.title == filename or cbz.title == Path(filename).name:
            # Title is same as full filename - probably failed to parse
            issues['title_is_filename'].append((filename, cbz))
        
        # Check if filename has "c###" but chapter wasn't extracted
        if 'c0' in filename.lower() or ' c1' in filename.lower() or ' c2' in filename.lower():
            if not cbz.chapter:
                issues['missed_chapter'].append((filename, cbz))
        
        # Check if filename has "v##" but volume wasn't extracted
        if ' v0' in filename.lower() or ' v1' in filename.lower():
            if not cbz.volume:
                issues['missed_volume'].append((filename, cbz))
    
    # Statistics
    print(f"\n📊 PARSING STATISTICS")
    print("=" * 80)
    print(f"Total files: {len(parsed_files)}")
    print(f"Files with title extracted: {sum(1 for cbz in parsed_files if cbz.title)}")
    print(f"Files with chapter: {sum(1 for cbz in parsed_files if cbz.chapter)}")
    print(f"Files with volume: {sum(1 for cbz in parsed_files if cbz.volume)}")
    print(f"Files with year: {sum(1 for cbz in parsed_files if cbz.year)}")
    print(f"Files with uploader: {sum(1 for cbz in parsed_files if cbz.uploader)}")
    print(f"Digital releases: {sum(1 for cbz in parsed_files if cbz.is_digital)}")
    print(f"One-shots: {sum(1 for cbz in parsed_files if cbz.is_oneshot)}")
    
    # Title distribution
    print(f"\n📚 TOP 10 TITLES BY FILE COUNT")
    print("=" * 80)
    title_counts = Counter(cbz.title for cbz in parsed_files if cbz.title)
    for title, count in title_counts.most_common(10):
        print(f"{count:4d} files - {title[:60]}")
    
    # Year distribution
    print(f"\n📅 FILES BY YEAR")
    print("=" * 80)
    year_counts = Counter(cbz.year for cbz in parsed_files if cbz.year)
    for year, count in sorted(year_counts.items()):
        print(f"{year}: {count:4d} files")
    
    # Issues found
    print(f"\n⚠️  POTENTIAL ISSUES")
    print("=" * 80)
    
    total_issues = sum(len(v) for v in issues.values())
    if total_issues == 0:
        print("✅ No issues found! All files parsed successfully.")
    else:
        for issue_type, items in issues.items():
            if items:
                print(f"\n{issue_type.upper().replace('_', ' ')}: {len(items)} files")
                print("-" * 80)
                # Show first 5 examples
                for filename, cbz in items[:5]:
                    print(f"  File: {Path(filename).name[:70]}")
                    print(f"    Title: {cbz.title}")
                    print(f"    Chapter: {cbz.chapter}, Volume: {cbz.volume}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")
    
    # Sample of well-parsed files
    print(f"\n✅ SAMPLE OF WELL-PARSED FILES (first 20)")
    print("=" * 80)
    for cbz in parsed_files[:20]:
        print(f"{cbz.display_name[:70]}")
    
    # Edge cases - files with special characters or unusual formats
    print(f"\n🔍 INTERESTING EDGE CASES")
    print("=" * 80)
    
    edge_cases = [
        cbz for cbz in parsed_files
        if ('/' in cbz.title or '／' in cbz.title) and cbz.title != "Unknown"
    ]
    if edge_cases:
        print(f"Files with slashes in title: {len(edge_cases)}")
        for cbz in edge_cases[:3]:
            print(f"  - {cbz.display_name[:70]}")
    
    decimal_chapters = [cbz for cbz in parsed_files if cbz.chapter and '.' in cbz.chapter]
    if decimal_chapters:
        print(f"\nFiles with decimal chapters: {len(decimal_chapters)}")
        for cbz in decimal_chapters[:3]:
            print(f"  - {cbz.display_name[:70]}")
    
    # Summary
    print(f"\n📈 SUMMARY")
    print("=" * 80)
    success_rate = ((len(parsed_files) - total_issues) / len(parsed_files)) * 100
    print(f"Parse success rate: {success_rate:.1f}%")
    print(f"Unique titles: {len(title_counts)}")
    print(f"Year range: {min(year_counts.keys()) if year_counts else 'N/A'} - {max(year_counts.keys()) if year_counts else 'N/A'}")
    print(f"Total issues: {total_issues}")


if __name__ == "__main__":
    main()
