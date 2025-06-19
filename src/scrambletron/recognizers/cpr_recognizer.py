"""CPRRecognizer with regex and validation."""

from datetime import datetime
from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class CPRRecognizer(PatternRecognizer):
    """Recognize cpr number using regex.

    Matches are validated based on the rules of the official CPR documentation:
    https://www.cpr.dk/media/12066/personnummeret-i-cpr.pdf
    Since not all valid CPR numbers are created with 'modulus 11 kontrol', the
    validation might falsely invalidate actual CPR numbers. See
    https://www.cpr.dk/cpr-systemet/personnumre-uden-kontrolciffer-modulus-11-kontrol

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
            seq_number = text[6:10]
        except ValueError:
            return False

        # Validate the date.
        try:
            datetime.strptime(f"{year}-{month}-{day}", "%y-%m-%d")
        except ValueError:
            return False

        self._verify_modulo_11(text, day, month, year, seq_number)

        return True

    # TODO: find a way to increase the score of the result instead of boolean
    def _verify_modulo_11(
        self, text: str, day: int, month: int, year: int, seq_number: str
    ) -> bool:
        """Verifies the CPR number using the 'modulus 11 kontrol'.

        Args:
            text: The full CPR number as a string.
            day: The day part of the CPR number.
            month: The month part of the CPR number.
            year: The year part of the CPR number.
            seq_number: The sequence number part of the CPR number.

        Returns:
            True if the CPR number passes the modulo 11 check, False otherwise.
        """
        # Derive the full year using the official CPR rules.
        try:
            full_year = self._derive_full_year(year, seq_number)
        except ValueError:
            return False

        # Validate the date using the derived full year.
        try:
            datetime.strptime(f"{full_year}-{month}-{day}", "%Y-%m-%d")
        except ValueError:
            return False

        # Calculate the check digit using weights for the first 9 digits.
        weights = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        total = sum(int(text[i]) * weights[i] for i in range(9))
        remainder = total % 11

        # Calculate computed check digit.
        if remainder == 0:
            computed_digit = 0
        else:
            computed_digit = 11 - remainder

        # If the computed check digit is 10, the number is considered invalid.
        if computed_digit == 10:
            return False

        # Finally, compare the computed check digit with the 10th digit.
        if computed_digit != int(text[9]):
            return False

        return True

    def _derive_full_year(self, year: int, seq_number: str) -> Optional[int]:
        """Derives the full year of a CPR number, based on the year and sequence number.

        Args:
            year: The two-digit year part of the CPR number.
            seq_number: The sequence number part of the CPR number.

        Returns:
            The full year if derived successfully, None otherwise.

        Raises:
            ValueError: If the CPR number is invalid.
        """
        try:
            digit7 = int(seq_number[0])
        except ValueError:
            raise ValueError("Invalid CPR: non-numeric characters found.")

        if 0 <= digit7 <= 3:
            return 1900 + year
        elif digit7 == 4 or digit7 == 9:
            if year <= 36:
                return 2000 + year
            elif year >= 36 and year <= 99:
                return 1900 + year
            else:
                raise ValueError("Invalid CPR number!")
        elif digit7 in [5, 6, 7, 8]:
            if year <= 57:
                return 2000 + year
            elif year >= 58 and year <= 99:
                return 1800 + year
            else:
                raise ValueError("Invalid CPR number!")
        else:
            raise ValueError("Invalid 7th digit.")
