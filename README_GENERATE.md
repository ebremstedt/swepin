# Generate Test Patients with Swedish Personal Identity Numbers (PINs)

This Python utility helps you generate realistic, valid Swedish Personal Identity Numbers (personnummer) for use in testing or development environments.

---

## Features

- Generate any number of valid PINs.
- Control birth year range for test data.
- Include coordination numbers (special variant of PIN).
- Control gender ratio (male/female distribution).
- Output as objects, dictionaries, or JSON strings.
- Optionally generate strict or loose PIN objects from the `swepin` library.

---

## Usage

### 1. Import the generator

```python
from swepin import generate_valid_pins


# Generate 20 random PINs, default options
pins = generate_valid_pins(count=20)

# Generate 50 PINs, only females (male_ratio=0.0), from 1950 to 2000
female_pins = generate_valid_pins(count=50, male_ratio=0.0, start_year=1950, end_year=2000)

# Generate 10 strict PIN objects with coordination numbers included
strict_pins = generate_valid_pins(count=10, strict=True, include_coordination_numbers=True)

# Generate 5 PINs as dictionaries (easy for JSON serialization)
pins_dicts = generate_valid_pins(count=5, to_dict=True)

# Generate 5 PINs as JSON strings
pins_json = generate_valid_pins(count=5, to_json=True)

# Example
from datetime import date
pins = generate_valid_pins(count=3)
for pin in pins:
    print(pin.pin)          # e.g. '19870714-2392'
    print(pin.male)         # True or False
    print(pin.female)       # True or False
    print(pin.year, pin.month, pin.day)

```
| Parameter                      | Type              | Default | Description                                              |
| ------------------------------ | ----------------- | ------- | -------------------------------------------------------- |
| `count`                        | `int`             | `10`    | Number of PINs to generate.                              |
| `start_year`                   | `int`             | `1920`  | Earliest birth year for generated PINs.                  |
| `end_year`                     | `int`             | `2024`  | Latest birth year for generated PINs.                    |
| `include_coordination_numbers` | `bool`            | `True`  | Whether to randomly include coordination numbers.        |
| `male_ratio`                   | `float` (0.0–1.0) | `0.5`   | Ratio of generated male PINs (e.g., 0.0 = all female).   |
| `today`                        | `date` or `None`  | `None`  | Reference date for age calculations (defaults to today). |
| `to_dict`                      | `bool`            | `False` | Return output as dictionaries instead of objects.        |
| `to_json`                      | `bool`            | `False` | Return output as JSON strings.                           |
| `strict`                       | `bool`            | `False` | Return `SwePinStrict` objects instead of `SwePinLoose`.  |
