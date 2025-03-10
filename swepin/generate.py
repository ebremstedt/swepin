import random
import datetime
from datetime import date
from swepin.swedish_personal_identity_number import (
    SwedishPersonalIdentityNumber,
    calculate_luhn_validation_digit,
)


def generate_valid_pins(
    count: int = 10,
    start_year: int = 1920,
    end_year: int = 2024,
    include_coordination_numbers: bool = True,
    include_centenarians: bool = True,
    male_ratio: float = 0.5,
    with_separator: bool = True,
    today: date | None = None,
    to_dict: bool = False,
    to_json: bool = False,
) -> list[SwedishPersonalIdentityNumber | dict | str]:
    """
    Generate a list of valid Swedish Personal Identity Numbers as objects.

    Args:
        count: Number of PINs to generate
        start_year: Earliest birth year to generate
        end_year: Latest birth year to generate
        include_coordination_numbers: Whether to include coordination numbers (day + 60)
        include_centenarians: Whether to include people over 100 years old
        male_ratio: Ratio of male PINs (0.0 to 1.0)
        with_separator: Whether to include separators in the output
        today: Reference date for age calculations (defaults to current date)
        to_dict: output as dictionaries
        to_json: output as json

    Returns:
        List of valid SwedishPersonalIdentityNumber objects
    """

    pins: list[SwedishPersonalIdentityNumber] = []
    today_date = today if today else date.today()

    while len(pins) < count:
        year = random.randint(start_year, end_year)
        is_centenarian = (today_date.year - year >= 100) and include_centenarians
        month = random.randint(1, 12)

        if month == 2:  # February
            if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):  # Leap year
                max_day = 29
            else:
                max_day = 28
        elif month in [4, 6, 9, 11]:  # 30-day months
            max_day = 30
        else:  # 31-day months
            max_day = 31

        day = random.randint(1, max_day)

        pin_date = datetime.date(year, month, day)
        if pin_date > today_date:
            continue

        is_coordination_number = random.random() < 0.1 and include_coordination_numbers
        display_day = day + 60 if is_coordination_number else day

        is_male = random.random() < male_ratio

        birth_place = random.randint(0, 99)
        gender_digit = (
            random.choice([1, 3, 5, 7, 9])
            if is_male
            else random.choice([0, 2, 4, 6, 8])
        )

        year_str = str(year)
        short_year = year_str[-2:]
        month_str = f"{month:02d}"
        day_str = f"{display_day:02d}"

        birth_number = f"{birth_place:02d}{gender_digit}"

        validation_digit = calculate_luhn_validation_digit(
            input_digits=f"{short_year}{month_str}{day_str}{birth_number}"
        )

        separator = "+" if is_centenarian else "-"

        if with_separator:
            pin_str = f"{short_year}{month_str}{day_str}{separator}{birth_number}{validation_digit}"
        else:
            pin_str = (
                f"{short_year}{month_str}{day_str}{birth_number}{validation_digit}"
            )

        pin_obj = SwedishPersonalIdentityNumber(pin_str, today=today_date)
        pins.append(pin_obj)

    if to_dict:
        return [pin.dict for pin in pins]

    if to_json:
        return [pin.json for pin in pins]

    return pins
