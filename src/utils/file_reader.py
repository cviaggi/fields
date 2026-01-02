"""File reading utilities for the Fields application."""

import os
from typing import Optional, List, Union
from pathlib import Path

try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class FileReader:
    """A utility class for reading files with various options."""

    def __init__(self, base_path: Optional[str] = None):
        """Initialize the FileReader.

        Args:
            base_path: Base directory for relative file paths
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def _resolve_path(self, file_path: Union[str, Path]) -> Path:
        """Resolve the full path for a given file path.

        Args:
            file_path: Path to resolve

        Returns:
            Resolved Path object
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.resolve()

    def _is_pdf_file(self, file_path: Union[str, Path]) -> bool:
        """Check if a file is a PDF based on its extension and content.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is a PDF, False otherwise
        """
        path = self._resolve_path(file_path)
        if not path.exists():
            return False

        # Check file extension
        if path.suffix.lower() == '.pdf':
            return True

        # Check file content (PDF files start with %PDF-)
        try:
            with open(path, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF-')
        except (OSError, IOError):
            return False

    def read_pdf_text(self, file_path: Union[str, Path]) -> str:
        """Read text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content from the PDF

        Raises:
            ImportError: If pypdf is not installed
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid PDF or cannot be read
        """
        if not PDF_SUPPORT:
            raise ImportError("PDF reading requires pypdf library. Install with: pip install pypdf")

        resolved_path = self._resolve_path(file_path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"PDF file not found: {resolved_path}")

        try:
            reader = PdfReader(str(resolved_path))
            text_content = []

            for page in reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)

            return '\n\n'.join(text_content)

        except Exception as e:
            raise ValueError(f"Error reading PDF file {resolved_path}: {e}")

    def read_pdf_pages(self, file_path: Union[str, Path]) -> List[str]:
        """Read text content from a PDF file, returning each page as a separate string.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of strings, one for each page

        Raises:
            ImportError: If pypdf is not installed
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid PDF or cannot be read
        """
        if not PDF_SUPPORT:
            raise ImportError("PDF reading requires pypdf library. Install with: pip install pypdf")

        resolved_path = self._resolve_path(file_path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"PDF file not found: {resolved_path}")

        try:
            reader = PdfReader(str(resolved_path))
            pages_content = []

            for page in reader.pages:
                text = page.extract_text()
                pages_content.append(text)

            return pages_content

        except Exception as e:
            raise ValueError(f"Error reading PDF file {resolved_path}: {e}")

    def read_file(self, file_path: Union[str, Path],
                  encoding: str = 'utf-8') -> str:
        """Read the entire content of a file.

        Args:
            file_path: Path to the file to read
            encoding: File encoding (default: utf-8, ignored for PDFs)

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            ImportError: If PDF reading is attempted without pypdf
            ValueError: If PDF reading fails
        """
        if self._is_pdf_file(file_path):
            return self.read_pdf_text(file_path)

        resolved_path = self._resolve_path(file_path)

        try:
            with open(resolved_path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {resolved_path}")
        except IOError as e:
            raise IOError(f"Error reading file {resolved_path}: {e}")

    def read_lines(self, file_path: Union[str, Path],
                   encoding: str = 'utf-8') -> List[str]:
        """Read a file and return its lines as a list.

        For PDF files, returns each page as a separate item in the list.

        Args:
            file_path: Path to the file to read
            encoding: File encoding (default: utf-8, ignored for PDFs)

        Returns:
            List of lines from the file (or pages for PDFs)
        """
        if self._is_pdf_file(file_path):
            return self.read_pdf_pages(file_path)

        content = self.read_file(file_path, encoding)
        return content.splitlines()

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        resolved_path = self._resolve_path(file_path)
        return resolved_path.exists() and resolved_path.is_file()

    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        resolved_path = self._resolve_path(file_path)

        if not resolved_path.exists():
            return {"exists": False}

        stat = resolved_path.stat()
        info = {
            "exists": True,
            "path": str(resolved_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": resolved_path.is_file(),
            "is_dir": resolved_path.is_dir(),
            "is_pdf": False,
            "pdf_pages": None
        }

        # Add PDF-specific information if it's a PDF file
        if info["is_file"] and self._is_pdf_file(resolved_path):
            info["is_pdf"] = True
            if PDF_SUPPORT:
                try:
                    reader = PdfReader(str(resolved_path))
                    info["pdf_pages"] = len(reader.pages)
                except Exception:
                    info["pdf_pages"] = "unknown"

        return info

    def find_files(self, pattern: str, directory: Optional[Union[str, Path]] = None) -> List[Path]:
        """Find files matching a pattern in a directory.

        Args:
            pattern: Glob pattern to match (e.g., "*.py", "**/*.txt")
            directory: Directory to search in (default: base_path)

        Returns:
            List of matching file paths
        """
        search_dir = self._resolve_path(directory) if directory else self.base_path

        if not search_dir.exists() or not search_dir.is_dir():
            return []

        return list(search_dir.glob(pattern))


# Global instance
_default_reader: Optional[FileReader] = None


def get_file_reader(base_path: Optional[str] = None) -> FileReader:
    """Get the default FileReader instance.

    Args:
        base_path: Base path for the reader

    Returns:
        FileReader instance
    """
    global _default_reader
    if _default_reader is None or (base_path and str(_default_reader.base_path) != base_path):
        _default_reader = FileReader(base_path)
    return _default_reader
