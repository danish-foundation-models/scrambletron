"""CPRRecognizer with regex and validation."""

from datetime import datetime
from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class CPRRecognizer(PatternRecognizer):
    """Recognize cpr number using regex.

    Validated using the CPR number validation algorithm, if

    Args:
        patterns: List of patterns to be used by this recognizer
        context: List of context words to increase confidence in detection
        supported_language: Language this recognizer supports
        supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern("DK_SSN1 (very weak)", r"\b[0-9]{10}\b", 0.05),
        Pattern("DK_SSN2 (very weak)", r"\b([0-9]{6})([0-9]{4})\b", 0.05),
        Pattern("DK_SSN3 (medium)", r"\b([0-9]{6})[-\s]([0-9]{4})\b", 0.5),
    ]

    CONTEXT = ["cpr", "cpr-nummer", "cpr nummer", "cpr-nr.", "cpr nr.", "personnummer"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "da",
        supported_entity: str = "DK_SSN",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        """Initialize the CPR recognizer."""
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [(" ", ""), ("-", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str):  # noqa D102
        # Clean the input
        text = EntityRecognizer.sanitize_value(pattern_text, self.replacement_pairs)

        if len(text) != 10 or not text.isdigit():
            return False

        # Extract parts: dd, mm, yy, løbenummer
        try:
            day = int(text[0:2])
            month = int(text[2:4])
            year = int(text[4:6])
            _seq_number = text[6:10]
        except ValueError:
            return False

        # Validate the date.
        try:
            datetime.strptime(f"{year}-{month}-{day}", "%y-%m-%d")
        except ValueError:
            return False

        return True
