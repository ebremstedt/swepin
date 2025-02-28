# SwePin

<div align="center">

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/swepin/)
[![Python versions](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://pypi.org/project/swepin/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/swepin)
[![Documentation](https://img.shields.io/badge/docs-latest-orange.svg)](https://swepin.readthedocs.io)

**A comprehensive library for parsing, validating, and handling Swedish Personal Identity Numbers (personnummer)**

</div>

## Overview

SwePin provides robust tools for working with Swedish Personal Identity Numbers, offering validation, parsing, and comprehensive information extraction. The library handles all formats of personal numbers, including standard formats, coordination numbers (samordningsnummer), and accounts for people over 100 years old.

## Installation

```bash
pip install swepin
```

## Quick Start

```python
# Import using the full name
from swepin import SwedishIdentityPersonalNumber

# Or using the shorter alias
from swepin import SwePin

# Parse a Swedish Personal Identity Number
pin = SwePin("198012241234")

# Get basic information
print(f"Birth date: {pin.get_date()}")          # 1980-12-24
print(f"Age: {pin.age}")                        # Current age based on today's date
print(f"Gender: {'Male' if pin.male else 'Female'}")

# Display detailed information
print(pin.pretty)                               # Prints a formatted table with all details

# Get structured data
pin_data = pin.dict                             # Dictionary representation
pin_json = pin.json                             # JSON representation
```

## Understanding Swedish Personal Identity Numbers

Swedish Personal Identity Numbers follow this format: `YYYYMMDD-XXXX` or `YYMMDD-XXXX` (or `+` instead of `-` for separator)

```
┌───────────────┬───────┬───────────────────┐
│  BIRTH DATE   │ SEP   │   BIRTH NUMBER    │
├───┬───┬───┬───┼───────┼───┬───┬───┬───────┤
│ C │ Y │ M │ D │ - / + │ B │ B │ G │ Valid │
└───┴───┴───┴───┴───────┴───┴───┴───┴───────┘
  │   │   │   │     │     │   │   │     │
  │   │   │   │     │     │   │   │     └── Validation Digit (Luhn algorithm)
  │   │   │   │     │     │   │   │
  │   │   │   │     │     │   │   └── Gender Digit (odd = male, even = female)
  │   │   │   │     │     │   │
  │   │   │   │     │     └───┴── Birth Place (regional code for pre-1990)
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

## Features

### Multiple Format Support

SwePin supports all standard formats of Swedish Personal Identity Numbers:

```python
# All these are valid and will parse correctly
SwePin("198012241234")    # Full format (12 digits)
SwePin("8012241234")      # Short format (10 digits)
SwePin("19801224-1234")   # With separator
SwePin("801224-1234")     # Short with separator
SwePin("19801284-1234")   # Coordination number (day 24 + 60 = 84)
SwePin("121212+1212")     # Person over 100 years old (+ separator)
```

### Format Conversion

Easily convert between different representations:

```python
pin = SwePin("198012241234")

# Access different format representations
print(pin.long_str_repr)                # "198012241234" (12 digits, no separator)
print(pin.long_str_repr_w_separator)    # "19801224-1234" (12 digits with separator)
print(pin.short_str_repr)               # "801224-1234" (10 digits with separator)
print(pin.short_str_repr_w_separator)   # "8012241234" (10 digits, no separator)
```

### Detailed Information

Get comprehensive information about a personal number with a beautiful formatted display:

```python
pin = SwePin("198012241234")
print(pin.pretty)
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Swedish Personal Identity Number Details                         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃         Property         ┃                 Value                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃      Original Number     ┃ 198012241234                           ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃        BIRTH DATE        ┃                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃         Century          ┃ 19                                     ┃
┃      Year (2 digits)     ┃ 80                                     ┃
┃    Full Year (4 digits)  ┃ 1980                                   ┃
┃          Month           ┃ 12                                     ┃
┃           Day            ┃ 24                                     ┃
┃         Full Date        ┃ 1980-12-24                             ┃
┃    Coordination Number   ┃ No                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃         SEPARATOR        ┃ -                                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃       BIRTH NUMBER       ┃                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃      Complete Number     ┃ 123                                    ┃
┃     Birth Place Digits   ┃ 12                                     ┃
┃       Gender Digit       ┃ 3                                      ┃
┃     Validation Digit     ┃ 4                                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃    DERIVED PROPERTIES    ┃                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃           Age            ┃ 44                                     ┃
┃          Gender          ┃ Male                                   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃         FORMATS          ┃                                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃      Long (12 digits)    ┃ 198012241234                           ┃
┃         Long (sep)       ┃ 19801224-1234                          ┃
┃  Short (10 digits) (sep) ┃ 801224-1234                            ┃
┃     Short without (sep)  ┃ 8012241234                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Validation

The library validates personal numbers using the Luhn algorithm to ensure the check digit is correct:

```python
try:
    pin = SwePin("198012241234")  # Valid personal number
    print("Valid personal identity number")
except Exception as e:
    print(f"Invalid: {e}")

try:
    pin = SwePin("198012241235")  # Invalid check digit
    print("Valid personal identity number")
except Exception as e:
    print(f"Invalid: {e}")  # Will print error about validation digit mismatch
```

### Special Cases

#### Coordination Numbers

For people without a permanent residence in Sweden, coordination numbers (samordningsnummer) are used where the day is increased by 60:

```python
pin = SwePin("198012841234")  # Day 24 + 60 = 84
print(f"Is coordination number: {pin._is_coordination_number()}")  # True
print(f"Birth date: {pin.get_date()}")  # Still returns 1980-12-24
```

#### Centenarians

For people 100 years or older, a `+` separator is used instead of `-` in the short format:

```python
pin = SwePin("121212+1212")  # Person born in 1912
print(pin.short_str_repr)    # "121212+1212"
print(pin.full_year)         # "1912"
```

## API Reference

### Main Class

`SwedishPersonalIdentityNumber` (alias: `SwePin`)

### Properties

| Property | Description |
|----------|-------------|
| `pin` | Original personal identity number string |
| `century` | Century part of birth year (e.g., "19") |
| `year` | Year part without century (e.g., "80") |
| `full_year` | Complete 4-digit year (e.g., "1980") |
| `month` | Month part (e.g., "12") |
| `day` | Day part (e.g., "24"), can be > 60 for coordination numbers |
| `separator` | Separator character ("-" or "+") |
| `birth_number` | 3-digit birth number, excluding validation digit |
| `birth_place` | Birth place code (first 2 digits of birth_number) |
| `gender_digit` | Gender digit (3rd digit of birth_number) |
| `validation_digit` | Validation digit calculated using Luhn algorithm |
| `age` | Calculated age based on birth date |
| `male` | Boolean indicating if the person is male |
| `female` | Boolean indicating if the person is female |
| `long_str_repr` | Full 12-digit representation without separator |
| `short_str_repr` | 10-digit representation with separator |
| `long_str_repr_w_separator` | Full 12-digit representation with separator |
| `short_str_repr_w_separator` | 10-digit representation without separator |
| `pretty` | Formatted tabular representation of all properties |
| `dict` | Dictionary representation of all properties |
| `json` | JSON string representation of all properties |

### Methods

| Method | Description |
|--------|-------------|
| `get_date()` | Returns a `datetime.date` object of the birth date |
| `get_age([today])` | Returns the current age, or age as of specified date |
| `_is_coordination_number()` | Returns `True` if this is a coordination number |
| `_is_male()` | Returns `True` if this is a male personal number |
| `pretty_print()` | Returns a nicely formatted table of all properties |
| `to_dict()` | Returns a dictionary representation |



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

<div align="center">
Made with ❤️ in Sweden
</div>