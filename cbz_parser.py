"""
CBZ Filename Parser

Parses various manga/comic filename formats to extract metadata like title, 
chapter, volume, year, uploader, etc.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Optional


@dataclass
class CBZFile:
    """
    Dataclass for parsing and storing CBZ filename metadata.
    
    Supports multiple naming formats:
    - Title CHAPTER# (YEAR) (Digital) (Uploader).cbz
    - Title - c### (v##) [Source] [Group].cbz
    - Title v## (YEAR) (Digital) (Uploader).cbz
    - Title - One-shot (YEAR) (Digital) (Uploader).cbz
    - Simple formats like v##.cbz
    """
    
    raw_filename: str
    fallback: bool = True
    title: Optional[str] = None
    chapter: Optional[str] = None
    volume: Optional[str] = None
    year: Optional[int] = None
    uploader: Optional[str] = None
    source: Optional[str] = None
    group: Optional[str] = None
    is_digital: bool = False
    is_oneshot: bool = False
    is_compilation: bool = False
    extra_tags: list[str] = field(default_factory=list)
    
    def __post_init__(self, fallback = True):
        """Parse the filename after initialization."""
        self.fallback=fallback
        self._parse_filename()
    
    def _parse_filename(self):
    
        """Parse the raw filename to extract metadata."""
        # Get the full path to extract folder context
        full_path = Path(self.raw_filename)
        
        # Get just the filename without path and extension
        cb_extensions = ('.cbz', '.cbr', '.cb7') 
        filename = full_path.name
        if full_path.suffix.casefold() in cb_extensions:
            filename = full_path.stem
        
        # Get parent folder name for context (useful for bare filenames)
        parent_folder = full_path.parent.name if full_path.parent.name != '.' else None
        
        # Check for "One-shot" pattern
        if re.search(r'\b[Oo]ne-shot\b', filename):
            self.is_oneshot = True
        
        # Check for digital
        if re.search(r'\([Dd]igital\)', filename):
            self.is_digital = True
        
        # Check for compilation indicators
        if re.search(r'\b[Cc]omplete\b|\b[Cc]ollection\b|\b[Cc]ompilation\b', filename):
            self.is_compilation = True
        
        # Try different parsing patterns in order of specificity
        
        # Pattern 1: "Title - c### (v##) [Source] [Group].cbz"
        # Example: Ah... and Mm... Are All She Says - c002 (v01) [Mangadex] [Gouma-Den]
        pattern1 = r'^(.+?)\s+-\s+c(\d+(?:\.\d+)?)\s+\(v(\d+)\)\s+\[([^\]]+)\]\s+\[([^\]]+)\]'
        match = re.match(pattern1, filename)
        if match:
            self.title = match.group(1).strip()
            self.chapter = match.group(2)
            self.volume = match.group(3)
            self.source = match.group(4)
            self.group = match.group(5)
            return
        
        # Pattern 2: "Title c### - Subtitle (YEAR) (Digital) (Uploader)"
        # Example: KAIJU NO.8 (Monster #8) c001 - Episode One - The Man Who Became a Monster (2020) (Digital) (Antrill)
        pattern2 = r'^(.+?)\s+c(\d+(?:\.\d+)?)\s+-\s+.+?\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern2, filename)
        if match:
            self.title = match.group(1).strip()
            self.chapter = match.group(2)
            self.year = int(match.group(3))
            self.uploader = match.group(4)
            return
        
        # Pattern 3: "Title c### (YEAR) (Digital) (Uploader)"
        # Example: The Lady Who Lied Her Way to Knighthood c001 (2021) (Digital) (Anon)
        pattern3 = r'^(.+?)\s+c(\d+(?:\.\d+)?)\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern3, filename)
        if match:
            self.title = match.group(1).strip()
            self.chapter = match.group(2)
            self.year = int(match.group(3))
            self.uploader = match.group(4)
            return
        
        # Pattern 4: "Title CHAPTER# (YEAR) (Digital) (Uploader)" (no 'c' prefix)
        # Example: Dandadan 149 (2024) (Digital) (1r0n)
        pattern4 = r'^(.+?)\s+(\d+(?:\.\d+)?)\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern4, filename)
        if match:
            # Verify the number isn't part of the title (like "3x3 Eyes")
            potential_title = match.group(1).strip()
            potential_chapter = match.group(2)
            
            # If the title doesn't end with a digit, this is likely a chapter number
            if not re.search(r'\d$', potential_title):
                self.title = potential_title
                self.chapter = potential_chapter
                self.year = int(match.group(3))
                self.uploader = match.group(4)
                return
        
        # Pattern 5: "Title v## (YEAR) (Digital) (Uploader)"
        # Example: Did I Seriously Just Get Reincarnated as My Gag Character v06 (2025) (Digital) (Ushi)
        pattern5 = r'^(.+?)\s+v(\d+)\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern5, filename)
        if match:
            self.title = match.group(1).strip()
            self.volume = match.group(2)
            self.year = int(match.group(3))
            self.uploader = match.group(4)
            return
        
        # Pattern 6: "Title - One-shot (YEAR) (Digital) (Uploader)"
        # Example: Echoes - One-shot (2025) (Digital) (Rillant)
        pattern6 = r'^(.+?)\s+-\s+[Oo]ne-shot\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern6, filename)
        if match:
            self.title = match.group(1).strip()
            self.year = int(match.group(2))
            self.uploader = match.group(3)
            return
        
        # Pattern 7: "Title (YEAR) (Digital) (Uploader)" (no chapter/volume)
        # Example: Farewell to My Alter (2021) (Digital) (1r0n)
        pattern7 = r'^(.+?)\s+\((\d{4})\)\s+\([Dd]igital\)\s+\(([^)]+)\)'
        match = re.match(pattern7, filename)
        if match:
            self.title = match.group(1).strip()
            self.year = int(match.group(2))
            self.uploader = match.group(3)
            return
        
        # Pattern 8: Simple "v##" format
        # Example: v01
        pattern8 = r'^v(\d+)$'
        match = re.match(pattern8, filename)
        if match:
            self.volume = match.group(1)
            # Try to get title from parent folder
            if parent_folder:
                # Clean up parent folder name (remove year ranges, tags, etc.)
                cleaned_title = re.sub(r'\s+\(\d{4}[-\d]*\).*$', '', parent_folder)
                cleaned_title = re.sub(r'\s+\([Dd]igital\).*$', '', cleaned_title)
                self.title = cleaned_title.strip()
            else:
                self.title = "Unknown"
            return
        
        # Pattern 9: Bare chapter format like "c152b"
        # Example: c152b
        pattern9 = r'^c(\d+)([a-z]?)$'
        match = re.match(pattern9, filename)
        if match:
            self.chapter = match.group(1) + (match.group(2) if match.group(2) else '')
            # Try to get title from parent folder
            if parent_folder:
                # Clean up parent folder name
                cleaned_title = re.sub(r'\s+\(\d{4}[-\d]*\).*$', '', parent_folder)
                cleaned_title = re.sub(r'\s+\([Dd]igital\).*$', '', cleaned_title)
                cleaned_title = re.sub(r'\s+\([^)]+\)$', '', cleaned_title)
                self.title = cleaned_title.strip()
            else:
                self.title = "Unknown"
            return
        
        # Pattern 10: Complex patterns with multiple parentheses and brackets
        # Try to extract year, uploader, and other tags
        year_match = re.search(r'\((\d{4})\)', filename)
        if year_match:
            self.year = int(year_match.group(1))
        
        # Extract content in parentheses (potential uploader)
        parens = re.findall(r'\(([^)]+)\)', filename)
        for paren in parens:
            if paren.lower() == 'digital':
                continue
            elif paren.isdigit() and len(paren) == 4:
                continue  # This is the year
            elif not self.uploader:
                self.uploader = paren
            else:
                self.extra_tags.append(paren)
        
        # Extract content in brackets (potential source/group)
        brackets = re.findall(r'\[([^\]]+)\]', filename)
        if brackets:
            if len(brackets) >= 1 and not self.source:
                self.source = brackets[0]
            if len(brackets) >= 2 and not self.group:
                self.group = brackets[1]
        
        # Try to extract chapter with 'c' prefix
        chapter_match = re.search(r'\bc(\d+(?:\.\d+)?)\b', filename)
        if chapter_match:
            self.chapter = chapter_match.group(1)
        
        # Try to extract volume
        volume_match = re.search(r'\bv(\d+)\b', filename, re.IGNORECASE)
        if volume_match and not self.volume:
            self.volume = volume_match.group(1)
        
        # Extract title (everything before first year, chapter, volume, or tag)
        if not self.title:
            # Remove known patterns from end
            title_candidate = filename
            title_candidate = re.sub(r'\s+\(\d{4}\).*$', '', title_candidate)
            title_candidate = re.sub(r'\s+[cv]\d+.*$', '', title_candidate, flags=re.IGNORECASE)
            title_candidate = re.sub(r'\s+\d+\s+\(.*$', '', title_candidate)
            title_candidate = re.sub(r'\s+-\s+[Oo]ne-shot.*$', '', title_candidate)
            
            if title_candidate:
                self.title = title_candidate.strip()
            else:
                if self.fallback:
                    self.title = filename  # Fallback to full filename
                else:
                    self.title = None
    
    @property
    def chapter_number(self) -> Optional[float]:
        """Get chapter as a numeric value (handles decimals like 282.1)."""
        if self.chapter:
            try:
                return float(self.chapter)
            except ValueError:
                return None
        return None
    
    @property
    def volume_number(self) -> Optional[int]:
        """Get volume as an integer."""
        if self.volume:
            try:
                return int(self.volume)
            except ValueError:
                return None
        return None
    
    @property
    def display_name(self) -> str:
        """Get a clean display name for the file."""
        parts = [self.title]
        
        if self.volume:
            parts.append(f"Vol. {self.volume}")
        
        if self.chapter:
            parts.append(f"Ch. {self.chapter}")
        
        if self.is_oneshot:
            parts.append("(One-shot)")
        
        if self.year:
            parts.append(f"({self.year})")
        
        return " ".join(parts)
    
    @property
    def sort_key(self) -> tuple:
        """
        Get a sort key for ordering files.
        Returns (title, volume_number, chapter_number, year).
        """
        return (
            self.title or "",
            self.volume_number or 0,
            self.chapter_number or 0,
            self.year or 0
        )
    
    def __repr__(self) -> str:
        """Custom representation showing key metadata."""
        parts = [f"CBZFile(title='{self.title}'"]
        if self.chapter:
            parts.append(f"chapter='{self.chapter}'")
        if self.volume:
            parts.append(f"volume='{self.volume}'")
        if self.year:
            parts.append(f"year={self.year}")
        if self.uploader:
            parts.append(f"uploader='{self.uploader}'")
        return ", ".join(parts) + ")"


def parse_cbz_filename(filename: str, fallback = True) -> CBZFile:
    """
    Convenience function to parse a CBZ filename.
    
    Args:
        filename: The CBZ filename (with or without path)
    
    Returns:
        CBZFile instance with parsed metadata
    
    Example:
        >>> cbz = parse_cbz_filename("Dandadan 149 (2024) (Digital) (1r0n).cbz")
        >>> print(cbz.title)
        'Dandadan'
        >>> print(cbz.chapter)
        '149'
        >>> print(cbz.year)
        2024
    """
    return CBZFile(raw_filename=filename, fallback=fallback)


if __name__ == "__main__":
    # Test with some example filenames
    test_files = [
        "'Tis Time for 'Torture,' Princess 282.1 (2025) (Digital) (Rillant).cbz",
        "Ah... and Mm... Are All She Says - c002 (v01) [Mangadex] [Gouma-Den].cbz",
        "The Lady Who Lied Her Way to Knighthood c001 (2021) (Digital) (Anon).cbz",
        "Dandadan 149 (2024) (Digital) (1r0n).cbz",
        "Did I Seriously Just Get Reincarnated as My Gag Character v06 (2025) (Digital) (Ushi).cbz",
        "Echoes - One-shot (2025) (Digital) (Rillant).cbz",
        "v01.cbz",
        "Farewell to My Alter (2021) (Digital) (1r0n).cbz",
    ]
    
    print("CBZ Filename Parser - Test Results")
    print("=" * 80)
    
    for filename in test_files:
        cbz = parse_cbz_filename(filename)
        print(f"\nFilename: {filename}")
        print(f"  Title: {cbz.title}")
        print(f"  Chapter: {cbz.chapter}")
        print(f"  Volume: {cbz.volume}")
        print(f"  Year: {cbz.year}")
        print(f"  Uploader: {cbz.uploader}")
        print(f"  Source: {cbz.source}")
        print(f"  Group: {cbz.group}")
        print(f"  Digital: {cbz.is_digital}")
        print(f"  One-shot: {cbz.is_oneshot}")
        print(f"  Display: {cbz.display_name}")
