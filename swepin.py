import datetime
import re
from datetime import date as Date
import json


class SwedishPersonalIdentityNumber:
    """
    A class for parsing, validating and handling Swedish Personal Identity Numbers (personnummer).

    ## Format Explanation

    Swedish Personal Identity Number follows the format: YYYYMMDD-XXXX or YYMMDD-XXXX

    ```
    ┌───────────────┬───────┬───────────────────┐
    │  BIRTH DATE   │ SEP   │   BIRTH NUMBER    │
    ├───┬───┬───┬───┼───────┼───┬───┬───┬───────┤
    │ C │ Y │ M │ D │ - / + │ B │ B │ G │ Valid │
    │ C │ Y │ M │ D │ - / + │ B │ B │ G │ Valid │
    └───┴───┴───┴───┴───────┴───┴───┴───┴───────┘
      │   │   │   │     │     │   │   │     │
      │   │   │   │     │     │   │   │     └── Validation Digit (calculated with Luhn algorithm)
      │   │   │   │     │     │   │   │
      │   │   │   │     │     │   │   └── Gender Digit (odd = male, even = female)
      │   │   │   │     │     │   │
      │   │   │   │     │     └───┴── Birth Place (historical regional code for pre-1990)
      │   │   │   │     │
      │   │   │   │     └── Separator (- if < 100 years old, + if >= 100)
      │   │   │   │
      │   │   │   └── Day (01-31, or 61-91 for coordination numbers)
      │   │   │
      │   │   └── Month (01-12)
      │   │
      │   └── Year (last two digits)
      │
      └── Century (optional in short format, derived when not provided)
    ```

    ## Examples

    Full format (12 digits): `198012241234`
    Short format (10 digits): `8012241234`
    With separators: `19801224-1234` or `801224-1234`
    Coordination number: `19801284-1234` (day 24 + 60 = 84)
    Person over 100: `191212121212` or `121212+1212`

    ## Instance Properties

    * `pin`: Original Personal Identity Number string provided
    * `century`: Century part of the birth year (e.g., "19")
    * `year`: Year part without century (e.g., "80")
    * `full_year`: Complete 4-digit year (e.g., "1980")
    * `month`: Month part (e.g., "12")
    * `day`: Day part (e.g., "24"), can be > 60 for coordination numbers
    * `separator`: Separator character ("-" or "+")
    * `birth_number`: 3-digit birth number, excluding check digit (e.g., "123")
    * `birth_place`: Birth place code (first 2 digits of birth_number, e.g., "12")
    * `gender_digit`: Gender digit (3rd digit of birth_number, e.g., "3")
    * `validation_digit`: Validation digit calculated using Luhn algorithm (e.g., "4")
    * `age`: Calculated age based on the birth date
    * `male`: Boolean indicating if the person is male
    * `female`: Boolean indicating if the person is female
    * `long_str_repr`: Full 12-digit representation without separator (e.g., "198012241234")
    * `short_str_repr`: 10-digit representation with separator (e.g., "801224-1234")
    * `long_str_repr_w_separator`: Full 12-digit representation with separator (e.g., "19801224-1234")
    * `short_str_repr_w_separator`: 10-digit representation without separator (e.g., "8012241234")
    * `pretty`: Formatted tabular representation of all properties

    ## Special Cases

    * **Coordination Numbers**: For people without a permanent residence in Sweden,
      the day number is increased by 60 (e.g., day 24 becomes 84).

    * **Centenarians**: People 100 years or older use a "+" separator instead of "-"
      in the short format.

    ## Usage Examples

    ```python
    # Parse a Swedish Personal Identity Number
    pin = SwedishPersonalNumber("198012241234")

    # Get the age
    age = pin.age  # 44 (assuming today is in 2024)

    # Check if male
    is_male = pin.male  # True if odd gender digit

    # Get birth date as Date object
    birth_date = pin.get_date()  # 1980-12-24

    # Different format representations
    full_no_sep = pin.long_str_repr           # "198012241234"
    short_with_sep = pin.short_str_repr       # "801224-1234"
    full_with_sep = pin.long_str_repr_w_separator    # "19801224-1234"
    short_no_sep = pin.short_str_repr_w_separator    # "8012241234"

    # Print a pretty table
    print(pin.pretty)
    ```
    """

    pin: str

    def __init__(self, pin):
        if not isinstance(pin, str):
            raise Exception("Swedish personal identity number must be a string")
        self.pin = pin

        self.century = None
        self.year = None
        self.month = None
        self.day = None
        self.separator = None
        self.birth_place = None
        self.gender_digit = None
        self.birth_number = None
        self.validation_digit = None
        self.age = None
        self.male = None
        self.female = None
        self.full_year = None
        self.long_str_repr = None
        self.short_str_repr = None
        self.long_str_repr_w_separator = None
        self.short_str_repr_w_separator = None
        self.pretty = None
        self.dict = None
        self.json = None

        self._parse_pin_parts()

        if not self.validation_digit:
            raise Exception("Validation digit is missing.")

        calculated_digit = self._calculate_validation_digit()
        if calculated_digit != int(self.validation_digit):
            raise Exception(
                f"Validation digit did not match the personal identity number. Expected {calculated_digit}, got {self.validation_digit}."
            )

        self.age = self.get_age()
        self.male = self._is_male()
        self.female = not self._is_male()

        year_month_day = f"{self.year}{self.month}{self.day}"
        self.long_str_repr = f"{self.century}{year_month_day}{self.birth_number}{self.validation_digit}"
        self.short_str_repr = f"{year_month_day}{self.separator}{self.birth_number}{self.validation_digit}"
        self.long_str_repr_w_separator = f"{self.century}{year_month_day}{self.separator}{self.birth_number}{self.validation_digit}"
        self.short_str_repr_w_separator = f"{year_month_day}{self.birth_number}{self.validation_digit}"
        self.pretty = self.pretty_print()
        self.dict = self.to_dict()
        self.json = json.dumps(self.dict)

    def _is_coordination_number(self):
        return int(self.day) > 60

    def get_date(self) -> Date:
        day = int(self.day)
        if self._is_coordination_number():
            day = day - 60
        return datetime.date(year=int(self.full_year), month=int(self.month), day=day)

    def get_age(self, today: Date = None) -> int:
        if today is None:
            today = datetime.date.today()

        day = int(self.day)
        if self._is_coordination_number():
            day = day - 60

        return (
            today.year
            - int(self.full_year)
            - ((today.month, today.day) < (int(self.month), day))
        )

    def _is_male(self) -> bool:
        gender_digit = int(self.birth_number[2])  # The third digit in the number part
        return gender_digit % 2 == 1  # Odd for males, even for females

    def _parse_pin_parts(self, today: Date = None):
        if today is None:
            today = datetime.date.today()

        reg = r"^(\d{2}){0,1}(\d{2})(\d{2})(\d{2})([\-\+]{0,1})?((\d{2})(\d{1}))((\d{1}))$"
        match = re.match(reg, str(self.pin))

        if not match:
            raise Exception(f'Could not parse "{self.pin}" as Swedish Personal Identity Number.')

        century = match.group(1)
        year = match.group(2)
        separator = match.group(5)

        if not century:
            base_year = today.year
            if separator == "+":
                base_year -= 100
            else:
                separator = "-"
            full_year = base_year - ((base_year - int(year)) % 100)
            century = str(int(full_year / 100))
        else:
            separator = "-" if today.year - int(century + year) < 100 else "+"

        self.century = century
        self.full_year = century + year
        self.year = year
        self.month = match.group(3)
        self.day = match.group(4)
        self.separator = separator
        self.birth_number = match.group(6)
        self.birth_place = match.group(7)
        self.gender_digit = match.group(8)
        self.validation_digit = match.group(10)

    def _calculate_validation_digit(self) -> int:
        """Calculate the validation digit for a Swedish personal number using the Luhn algorithm."""
        # Combine all digits except the validation digit
        input_digits = f"{self.year}{self.month}{self.day}{self.birth_number}"
        total_sum = 0
        # Process each digit according to Luhn algorithm
        for position, digit in enumerate(input_digits):
            value = int(digit)
            # Multiply every other digit by 2, starting from the right
            # This is reversed from the usual description because we're working from left to right
            # In the original Luhn algorithm, multiplication by 2 starts from the rightmost digit
            if position % 2 == 0:
                value *= 2  # Positions 0, 2, 4, etc. get doubled
            else:
                value *= 1  # Positions 1, 3, 5, etc. remain unchanged
            # If doubling results in a two-digit number, subtract 9
            # This is equivalent to adding the digits together (e.g., 14 -> 1+4=5 or 14-9=5)
            if value > 9:
                value -= 9

            total_sum += value

        # Calculate the validation digit: the number needed to make the sum divisible by 10
        return (10 - (total_sum % 10)) % 10

    def __str__(self):
        return self.short_str_repr

    # fmt: off
    def pretty_print(self) -> str:
        """
        Returns a nicely formatted table displaying all properties of the Swedish Personal Identity Number.

        Returns:
            str: A multi-line string containing the formatted table
        """
        # Define the maximum width for property names and values
        prop_width = 28
        val_width = 40

        # Prepare a list to hold all lines of the table
        lines = []

        # Build header
        lines.append("┏" + "━" * prop_width + "┳" + "━" * val_width + "┓")
        title = "Swedish Personal Identity Number Details"
        # Calculate the exact space needed for proper centering
        title_padding = prop_width + val_width + 1 - len(title)
        left_pad = title_padding // 2
        right_pad = title_padding - left_pad
        lines.append("┃" + " " * left_pad + title + " " * right_pad + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add property and value header
        lines.append("┃" + f" {'Property':^{prop_width-2}} " + "┃" + f" {'Value':^{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add the original PIN
        lines.append("┃" + f" {'Original Number':^{prop_width-2}} " + "┃" + f" {self.pin:<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add birth date section
        lines.append("┃" + f" {'BIRTH DATE':^{prop_width-2}} " + "┃" + f" {'':<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")
        lines.append("┃" + f" {'  Century':^{prop_width-2}} " + "┃" + f" {self.century:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Year (2 digits)':^{prop_width-2}} " + "┃" + f" {self.year:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Full Year (4 digits)':^{prop_width-2}} " + "┃" + f" {self.full_year:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Month':^{prop_width-2}} " + "┃" + f" {self.month:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Day':^{prop_width-2}} " + "┃" + f" {self.day:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Full Date':^{prop_width-2}} " + "┃" + f" {self.get_date().strftime('%Y-%m-%d'):<{val_width-2}} " + "┃")

        # Always show coordination number information
        is_coord = self._is_coordination_number()
        if is_coord:
            lines.append("┃" + f" {'  Coordination Number':^{prop_width-2}} " + "┃" + f" {'Yes (day + 60)':<{val_width-2}} " + "┃")
            lines.append("┃" + f" {'  Actual Day':^{prop_width-2}} " + "┃" + f" {str(int(self.day) - 60):<{val_width-2}} " + "┃")
        else:
            lines.append("┃" + f" {'  Coordination Number':^{prop_width-2}} " + "┃" + f" {'No':<{val_width-2}} " + "┃")

        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add separator section
        lines.append("┃" + f" {'SEPARATOR':^{prop_width-2}} " + "┃" + f" {self.separator:<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add birth number section
        lines.append("┃" + f" {'BIRTH NUMBER':^{prop_width-2}} " + "┃" + f" {'':<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")
        lines.append("┃" + f" {'  Complete Number':^{prop_width-2}} " + "┃" + f" {self.birth_number:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Birth Place Digits':^{prop_width-2}} " + "┃" + f" {self.birth_place:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Gender Digit':^{prop_width-2}} " + "┃" + f" {self.gender_digit:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Validation Digit':^{prop_width-2}} " + "┃" + f" {self.validation_digit:<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")

        # Add derived properties section
        lines.append("┃" + f" {'DERIVED PROPERTIES':^{prop_width-2}} " + "┃" + f" {'':<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")
        lines.append("┃" + f" {'  Age':^{prop_width-2}} " + "┃" + f" {self.age:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Gender':^{prop_width-2}} " + "┃" + f" {'Male' if self.male else 'Female':<{val_width-2}} " + "┃")

        # Format section with all combinations
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")
        lines.append("┃" + f" {'FORMATS':^{prop_width-2}} " + "┃" + f" {'':<{val_width-2}} " + "┃")
        lines.append("┣" + "━" * prop_width + "╋" + "━" * val_width + "┫")
        lines.append("┃" + f" {'  Long (12 digits) w/o sep':^{prop_width-2}} " + "┃" + f" {self.long_str_repr:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Long w/ separator':^{prop_width-2}} " + "┃" + f" {self.long_str_repr_w_separator:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Short (10 digits) w/ sep':^{prop_width-2}} " + "┃" + f" {self.short_str_repr:<{val_width-2}} " + "┃")
        lines.append("┃" + f" {'  Short w/o separator':^{prop_width-2}} " + "┃" + f" {self.short_str_repr_w_separator:<{val_width-2}} " + "┃")

        # Add footer
        lines.append("┗" + "━" * prop_width + "┻" + "━" * val_width + "┛")

        # Join all lines with newlines and return the result
        return "\n".join(lines)
    # fmt: on

    def to_dict(self) -> dict:
        data = {
            "personal_identity_number": self.pin,
            "birth_date": {
                "century": self.century,
                "year": self.year,
                "full_year": self.full_year,
                "month": self.month,
                "day": self.day,
                "iso_date": self.get_date().isoformat(),
            },
            "separator": self.separator,
            "birth_number": {
                "complete": self.birth_number,
                "birth_place": self.birth_place,
                "gender_digit": self.gender_digit,
            },
            "validation_digit": self.validation_digit,
            "derived_info": {
                "age": self.age,
                "gender": "male" if self.male else "female",
                "is_coordination_number": self._is_coordination_number(),
            },
            "formats": {
                "long_format": self.long_str_repr,
                "short_format": self.short_str_repr,
            },
        }
        if data["derived_info"]["is_coordination_number"]:
            data["birth_date"]["actual_day"] = int(self.day) - 60

        return data