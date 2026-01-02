"""Permit summarization utilities for the Fields application."""

import re
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from .file_reader import get_file_reader
from .logger import get_logger


class SummarizePermit:
    """A class for summarizing permit-related information and documents."""

    def __init__(self, base_path: Optional[str] = None):
        """Initialize the SummarizePermit class.

        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.logger = get_logger("SummarizePermit")
        self.file_reader = get_file_reader(str(self.base_path))

    def summarize_from_file(self, file_path: Union[str, Path],
                          max_length: int = 500) -> Dict[str, Any]:
        """Summarize permit information from a file.

        Args:
            file_path: Path to the file containing permit information
            max_length: Maximum length of the summary

        Returns:
            Dictionary containing summary information
        """
        self.logger.debug(f"Summarizing permit from file: {file_path}")

        try:
            # Read the file content
            content = self.file_reader.read_file(file_path)

            # Get file information
            file_info = self.file_reader.get_file_info(file_path)
            
            # Extract patterns and basic summary
            extracted_data = self._extract_basic_summary(content, max_length)
            
            # Create a basic text summary for backward compatibility
            if len(content) <= 500:
                summary = content
            else:
                summary = content[:500] + "..."

            result = {
                "file_path": str(file_info["path"]),
                "file_type": "pdf" if file_info.get("is_pdf", False) else "text",
                "summary": summary,
                "date_time_slots": extracted_data['date_time_slots'],
                "field_names": extracted_data['field_names'],
                "field_date_time_slots": extracted_data['field_date_time_slots'],
                "word_count": len(content.split()),
                "character_count": len(content),
                "pages": file_info.get("pdf_pages") if file_info.get("is_pdf") else 1,
                "success": True
            }

            self.logger.info(f"Successfully summarized permit from {file_path}")
            return result

        except Exception as e:
            self.logger.error(f"Error summarizing permit from {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "error": str(e),
                "success": False
            }

    def summarize_from_text(self, text: str, title: str = "Permit Document",
                          max_length: int = 500) -> Dict[str, Any]:
        """Summarize permit information from text content.

        Args:
            text: Text content to summarize
            title: Title for the document
            max_length: Maximum length of the summary

        Returns:
            Dictionary containing summary information
        """
        self.logger.debug(f"Summarizing permit from text: {title}")

        try:
            # Extract patterns
            extracted_data = self._extract_basic_summary(text, max_length)

            # Create a basic text summary for backward compatibility
            if len(text) <= 500:
                summary = text
            else:
                summary = text[:500] + "..."

            result = {
                "title": title,
                "summary": summary,
                "date_time_slots": extracted_data['date_time_slots'],
                "field_names": extracted_data['field_names'],
                "field_date_time_slots": extracted_data['field_date_time_slots'],
                "word_count": len(text.split()),
                "character_count": len(text),
                "success": True
            }

            self.logger.info(f"Successfully summarized permit from text: {title}")
            return result

        except Exception as e:
            self.logger.error(f"Error summarizing permit from text {title}: {e}")
            return {
                "title": title,
                "error": str(e),
                "success": False
            }

    def _extract_basic_summary(self, text: str, max_length: int) -> Dict[str, List[str]]:
        """Extract lines containing date/time patterns and field names from text content.

        Looks for:
        - Date/time patterns: "Sat, Dec 6, 2025 8:00 AM Sat, Dec 6, 2025 1:00 PM"
        - Field names: "Shoreline North Field (Athletic Field Use)"

        Args:
            text: Text content to analyze
            max_length: Maximum number of matching items to return for each category

        Returns:
            Dictionary with 'date_time_slots' and 'field_names' lists
        """
        # Regex patterns
        # Date/time pattern: Day, Month Day, Year Time AM/PM (can repeat)
        date_time_pattern = r'^[A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4} \d{1,2}:\d{2} (?:AM|PM)(?: [A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4} \d{1,2}:\d{2} (?:AM|PM))*\s'

        # Field name pattern: Word+ Field (Description in parentheses)
        field_name_pattern = r'^[A-Za-z\s]+ \(Athletic Field Use\)'


        # Split text into lines and filter for patterns
        lines = text.split('\n')
        current_field_name = None
        field_date_time_slots = {}
        date_time_slots = []
        field_names = []

        for line in lines:
            
            line = line.strip()
            self.logger.debug(f"Processing line: {line}")

            if not line:
                continue

            # Check for date/time patterns
            if re.match(date_time_pattern, line) and len(date_time_slots) < max_length:
                date_time_slots.append(line)
                field_date_time_slots[current_field_name].append(line)

            # Check for field name patterns
            elif re.match(field_name_pattern, line) and len(field_names) < max_length:
                field_names.append(line)
                field_date_time_slots[line] = []
                current_field_name = line

        self.logger.debug(f"Found {len(date_time_slots)} date/time slots and {len(field_names)} field names")
        return {
            'date_time_slots': date_time_slots,
            'field_names': field_names,
            'field_date_time_slots': field_date_time_slots
        }

    def batch_summarize(self, file_paths: List[Union[str, Path]],
                       max_length: int = 500) -> List[Dict[str, Any]]:
        """Summarize multiple permit files.

        Args:
            file_paths: List of file paths to summarize
            max_length: Maximum length for each summary

        Returns:
            List of summary dictionaries
        """
        self.logger.debug(f"Batch summarizing {len(file_paths)} files")

        results = []
        for file_path in file_paths:
            summary = self.summarize_from_file(file_path, max_length)
            results.append(summary)

        successful = sum(1 for r in results if r.get("success", False))
        self.logger.info(f"Batch summarization complete: {successful}/{len(file_paths)} successful")

        return results

    def find_permit_files(self, directory: Union[str, Path]) -> List[Path]:
        """Find potential permit files in a directory.

        Args:
            directory: Directory to search

        Returns:
            List of file paths that might contain permit information
        """
        self.logger.debug(f"Finding permit files in: {directory}")

        # Common permit-related file patterns
        patterns = [
            "*.pdf", "*.txt", "*.doc", "*.docx",
            "*permit*", "*license*", "*application*"
        ]

        found_files = []
        for pattern in patterns:
            matches = self.file_reader.find_files(pattern, directory)
            found_files.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for file_path in found_files:
            if str(file_path) not in seen:
                seen.add(str(file_path))
                unique_files.append(file_path)

        self.logger.info(f"Found {len(unique_files)} potential permit files")
        return unique_files
