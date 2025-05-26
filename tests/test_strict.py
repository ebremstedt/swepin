import pytest
from datetime import date
from swepin import SwePinStrict, Language


class TestSwePinStrictValidFormats:
    """Test cases for valid SwePinStrict formats."""

    def test_valid_format_regular_number(self):
        """Test valid regular personal number in strict format."""
        pin = SwePinStrict("19801224-1234")
        assert pin.pin == "19801224-1234"
        assert pin.century == "19"
        assert pin.year == "80"
        assert pin.full_year == "1980"
        assert pin.month == "12"
        assert pin.day == "24"
        assert pin.separator == "-"
        assert pin.birth_number == "123"
        assert pin.validation_digit == "4"

    def test_valid_format_coordination_number(self):
        """Test valid coordination number in strict format."""
        pin = SwePinStrict("19801284-1230")  # Day 24 + 60 = 84
        assert pin.pin == "19801284-1230"
        assert pin.day == "84"
        assert pin.is_coordination_number == True
        assert pin.calculated_day_from_coordination_number == "24"

    def test_valid_format_different_years(self):
        """Test valid format with different years."""
        test_cases = [
            "20001201-1234",  # 2000s
            "19501015-5678",  # 1950s
            "20251231-9876",  # Future year
        ]

        for pin_str in test_cases:
            # Calculate correct validation digit for each
            from swepin.swedish_personal_identity_number import calculate_luhn_validation_digit
            base_digits = pin_str.replace("-", "")[2:-1]  # Remove century and last digit
            correct_digit = calculate_luhn_validation_digit(base_digits)
            valid_pin = pin_str[:-1] + str(correct_digit)

            pin = SwePinStrict(valid_pin)
            assert pin.pin == valid_pin

    def test_inherited_functionality(self):
        """Test that all inherited functionality works correctly."""
        pin = SwePinStrict("19801224-1234")

        # Test properties
        assert isinstance(pin.birth_date, date)
        assert pin.birth_date == date(1980, 12, 24)
        assert isinstance(pin.age, int)
        assert pin.male == True  # Gender digit 3 is odd
        assert pin.female == False

        # Test format representations
        assert pin.long_str_repr == "198012241234"
        assert pin.short_str_repr == "801224-1234"
        assert pin.long_str_repr_w_separator == "19801224-1234"
        assert pin.short_str_repr_w_separator == "8012241234"


class TestSwePinStrictInvalidFormats:
    """Test cases for invalid SwePinStrict formats."""

    def test_reject_short_format_with_separator(self):
        """Test rejection of short format with separator."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict("801224-1234")
        assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_long_format_without_separator(self):
        """Test rejection of long format without separator."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict("198012241234")
        assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_short_format_without_separator(self):
        """Test rejection of short format without separator."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict("8012241234")
        assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_plus_separator(self):
        """Test rejection of plus separator."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict("19801224+1234")
        assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_wrong_length(self):
        """Test rejection of wrong length strings."""
        invalid_lengths = [
            "1980122-1234",      # Too short
            "198012241-1234",    # Too long before separator
            "19801224-12345",    # Too long after separator
            "19801224-123",      # Too short after separator
            "198012241234567",   # Way too long
            "1234-1234",         # Way too short
        ]

        for invalid_pin in invalid_lengths:
            with pytest.raises(Exception) as exc_info:
                SwePinStrict(invalid_pin)
            assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_non_numeric_parts(self):
        """Test rejection of non-numeric parts."""
        invalid_pins = [
            "ABCD1224-1234",     # Letters in year
            "198O1224-1234",     # Letter O instead of 0
            "19801224-ABCD",     # Letters in birth number
            "19801224-123A",     # Letter in validation digit
        ]

        for invalid_pin in invalid_pins:
            with pytest.raises(Exception) as exc_info:
                SwePinStrict(invalid_pin)
            assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_wrong_separator_position(self):
        """Test rejection of separator in wrong position."""
        invalid_pins = [
            "1980-1224-1234",    # Multiple separators
            "19801-224-1234",    # Separator in wrong position
            "1980122-4-1234",    # Separator in wrong position
        ]

        for invalid_pin in invalid_pins:
            with pytest.raises(Exception) as exc_info:
                SwePinStrict(invalid_pin)
            assert 'does not match strict format YYYYMMDD-NNNN' in str(exc_info.value)

    def test_reject_non_string_input(self):
        """Test rejection of non-string input."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict(198012241234)
        assert "Swedish personal identity number must be a string" in str(exc_info.value)

    def test_reject_invalid_luhn_validation(self):
        """Test rejection of invalid Luhn validation digit."""
        with pytest.raises(Exception) as exc_info:
            SwePinStrict("19801224-1235")  # Wrong validation digit
        assert "Validation digit did not match" in str(exc_info.value)


class TestSwePinStrictEdgeCases:
    """Test edge cases for SwePinStrict."""

    def test_coordination_numbers(self):
        """Test coordination numbers work correctly in strict format."""
        # Test various coordination number days (61-91)
        coordination_days = ["61", "75", "84", "91"]

        for coord_day in coordination_days:
            # Generate a valid PIN with coordination number
            base_digits = f"80122{coord_day}123"
            from swepin.swedish_personal_identity_number import calculate_luhn_validation_digit
            validation_digit = calculate_luhn_validation_digit(base_digits)
            pin_str = f"19801{coord_day[1:]}{coord_day}-123{validation_digit}"

            pin = SwePinStrict(pin_str)
            assert pin.is_coordination_number == True
            assert int(pin.calculated_day_from_coordination_number) == int(coord_day) - 60

    def test_leap_year_dates(self):
        """Test leap year dates in strict format."""
        # February 29th in leap year
        from swepin.swedish_personal_identity_number import calculate_luhn_validation_digit
        base_digits = "80022912"
        validation_digit = calculate_luhn_validation_digit(base_digits + "3")
        pin_str = f"19800229-123{validation_digit}"

        pin = SwePinStrict(pin_str)
        assert pin.birth_date == date(1980, 2, 29)

    def test_custom_reference_date(self):
        """Test SwePinStrict with custom reference date."""
        reference_date = date(2020, 1, 1)
        pin = SwePinStrict("19801224-1234", today=reference_date)

        expected_age = 2020 - 1980 - 1  # Birthday hasn't occurred yet in 2020
        assert pin.age == expected_age
        assert pin.today == reference_date


class TestSwePinStrictFormatProperties:
    """Test format property consistency in SwePinStrict."""

    def test_format_consistency(self):
        """Test that all format properties are consistent."""
        pin = SwePinStrict("19801224-1234")

        # Test that the strict format is always maintained in certain properties
        assert pin.long_str_repr_w_separator == "19801224-1234"  # Should match input
        assert len(pin.long_str_repr) == 12  # Should be 12 digits
        assert len(pin.short_str_repr) == 11  # Should be 10 digits + separator
        assert "-" in pin.short_str_repr
        assert "-" not in pin.long_str_repr
        assert "-" not in pin.short_str_repr_w_separator

    def test_separator_always_dash(self):
        """Test that separator is always dash in strict mode."""
        pin = SwePinStrict("19801224-1234")
        assert pin.separator == "-"

        # Even for very old people, separator should be dash in strict mode
        pin_old = SwePinStrict("19121212-1216")  # Someone born in 1912
        assert pin_old.separator == "-"


class TestSwePinStrictLanguageSupport:
    """Test language support for SwePinStrict."""

    def test_english_output(self):
        """Test English language output."""
        pin = SwePinStrict("19801224-1234")

        pretty_en = pin.pretty_print(language=Language.ENG)
        assert "Swedish Personal Identity Number" in pretty_en
        assert "Original Number" in pretty_en

        dict_en = pin.to_dict(language=Language.ENG)
        assert "personal_identity_number" in dict_en
        assert "birth_date" in dict_en

    def test_swedish_output(self):
        """Test Swedish language output."""
        pin = SwePinStrict("19801224-1234")

        pretty_sv = pin.pretty_print(language=Language.SWE)
        assert "Svenskt Personnummer" in pretty_sv
        assert "Ursprungligt personnummer" in pretty_sv

        dict_sv = pin.to_dict(language=Language.SWE)
        assert "personnummer" in dict_sv
        assert "födelsedatum" in dict_sv

    def test_json_output(self):
        """Test JSON output for SwePinStrict."""
        pin = SwePinStrict("19801224-1234")

        import json
        json_data = json.loads(pin.json)
        assert "personal_identity_number" in json_data
        assert json_data["personal_identity_number"] == "19801224-1234"


class TestSwePinStrictVsRegularSwePin:
    """Test differences between SwePinStrict and regular SwePin."""

    def test_strict_rejects_what_regular_accepts(self):
        """Test that SwePinStrict rejects formats that regular SwePin accepts."""
        from swepin import SwePin

        flexible_formats = [
            "801224-1234",      # Short with separator
            "198012241234",     # Long without separator
            "8012241234",       # Short without separator
        ]

        for pin_str in flexible_formats:
            # Regular SwePin should accept these
            regular_pin = SwePin(pin_str)
            assert regular_pin is not None

            # SwePinStrict should reject these
            with pytest.raises(Exception):
                SwePinStrict(pin_str)

    def test_both_accept_strict_format(self):
        """Test that both classes accept the strict format."""
        from swepin import SwePin

        strict_format = "19801224-1234"

        # Both should accept this format
        regular_pin = SwePin(strict_format)
        strict_pin = SwePinStrict(strict_format)

        # They should have the same parsed values
        assert regular_pin.pin == strict_pin.pin
        assert regular_pin.birth_date == strict_pin.birth_date
        assert regular_pin.age == strict_pin.age
        assert regular_pin.male == strict_pin.male


if __name__ == "__main__":
    pytest.main([__file__])