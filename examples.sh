#!/bin/bash
# Example usage of parse_cbz.py

echo "=== Example 1: Simple parsing ==="
./parse_cbz.py "Dandadan 149 (2024) (Digital) (1r0n).cbz" --pretty

echo -e "\n=== Example 2: Extract just the title with jq ==="
./parse_cbz.py "One Piece 1100 (2024) (Digital) (1r0n).cbz" | jq -r '.title'

echo -e "\n=== Example 3: Extract multiple fields ==="
./parse_cbz.py "KAIJU NO.8 (Monster #8) c001 - Episode One (2020) (Digital) (Antrill).cbz" | jq -r '"\(.title) - Chapter \(.chapter) (\(.year))"'

echo -e "\n=== Example 4: Batch processing with while loop ==="
head -3 cbz_files.txt | while read file; do 
    ./parse_cbz.py "$file" | jq -r '.display_name'
done

echo -e "\n=== Example 5: Filter by year ==="
for file in $(head -10 cbz_files.txt); do
    year=$(./parse_cbz.py "$file" | jq -r '.year // empty')
    if [ "$year" = "2025" ]; then
        ./parse_cbz.py "$file" | jq -r '.display_name'
    fi
done

echo -e "\n=== Example 6: Check if file is digital ==="
./parse_cbz.py "Dandadan 149 (2024) (Digital) (1r0n).cbz" | jq -r 'if .is_digital then "Digital" else "Physical" end'
