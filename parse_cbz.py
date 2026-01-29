#!/usr/bin/env python3
"""
CLI tool to parse CBZ filenames and output JSON.

Usage:
    ./parse_cbz.py <filename>
    ./parse_cbz.py <filename> [--pretty]
    
Examples:
    ./parse_cbz.py "Dandadan 149 (2024) (Digital) (1r0n).cbz"
    ./parse_cbz.py "./Freesia/v01.cbz" --pretty
    cat cbz_files.txt | xargs -I {} ./parse_cbz.py "{}"
    ./parse_cbz.py "file.cbz" | jq '.title'
"""

import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from cbz_parser import parse_cbz_filename

logger = logging.getLogger('process')

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        sys.exit(0)
    
    filename = sys.argv[1]
    pretty = '--pretty' in sys.argv or '-p' in sys.argv
    debug = '--debug' in sys.argv or '-d' in sys.argv

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    

    
    # Parse the filename
    cbz = parse_cbz_filename(filename)
    
    # Convert to dict
    result = {
        'raw_filename': cbz.raw_filename,
        'title': cbz.title,
        'chapter': cbz.chapter,
        'chapter_number': cbz.chapter_number,
        'volume': cbz.volume,
        'volume_number': cbz.volume_number,
        'annual': cbz.annual,
        'special': cbz.special,
        'year': cbz.year,
        'uploader': cbz.uploader,
        'source': cbz.source,
        'group': cbz.group,
        'is_digital': cbz.is_digital,
        'is_oneshot': cbz.is_oneshot,
        'is_compilation': cbz.is_compilation,
        'extra_tags': cbz.extra_tags,
        'display_name': cbz.display_name,
    }
    
    # Output JSON
    if pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
