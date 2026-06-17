"""
Base parser interface. All document parsers implement this protocol.
"""
from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Abstract document parser."""

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from a document file.

        Args:
            file_path: Absolute path to the file.

        Returns:
            The extracted plain text.

        Raises:
            ParseFailureException: If the file cannot be read/parsed.
        """
        ...
