import re
from swepin.swedish_personal_identity_number import SwedishPersonalIdentityNumber
from datetime import date as Date


class SwePinStrict(SwedishPersonalIdentityNumber):
    """
    A strict version of SwedishPersonalIdentityNumber that only accepts the format YYYYMMDD-NNNN.

    This class enforces:
    - Exactly 13 characters total
    - Full 4-digit year (YYYY)
    - Dash separator only (no plus sign)
    - Format: YYYYMMDD-NNNN

    Examples of valid formats:
    - 19801224-1234
    - 19801284-1234 (coordination number)

    Examples of invalid formats (will raise exception):
    - 801224-1234 (missing century)
    - 198012241234 (no separator)
    - 19801224+1234 (plus separator not allowed)
    - 1980-12-24-1234 (wrong format)
    """

    def __init__(self, pin: str, today: Date | None = None):
        if not isinstance(pin, str):
            raise Exception("Swedish personal identity number must be a string")

        if not self._validate_strict_format(pin):
            raise Exception(
                f'"{pin}" does not match strict format YYYYMMDD-NNNN. '
                f'Expected exactly 13 characters with format like "19801224-1234"'
            )

        super().__init__(pin, today)

    def _validate_strict_format(self, pin: str) -> bool:
        """Validate that PIN matches exactly YYYYMMDD-NNNN format."""
        if len(pin) != 13:
            return False

        strict_pattern = r"^(\d{4})(\d{2})(\d{2})-(\d{3})(\d{1})$"
        match = re.match(strict_pattern, pin)
        return match is not None

    def _parse_pin_parts(self):
        """Override parent method to use strict parsing."""
        strict_pattern = r"^(\d{4})(\d{2})(\d{2})-(\d{3})(\d{1})$"
        match = re.match(strict_pattern, str(self.pin))

        if not match:
            raise Exception(
                f'Could not parse "{self.pin}" with strict format YYYYMMDD-NNNN.'
            )

        full_year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        birth_number = match.group(4)
        validation_digit = match.group(5)

        self.century = full_year[:2]
        self.year = full_year[2:]
        self.full_year = full_year
        self.month = month
        self.day = day
        self.separator = "-"
        self.birth_number = birth_number
        self.birth_place = birth_number[:2]
        self.gender_digit = birth_number[2]
        self.validation_digit = validation_digit