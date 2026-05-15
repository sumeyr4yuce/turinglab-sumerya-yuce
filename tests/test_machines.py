from pathlib import Path

import pytest

from turinglab import SingleTapeTM


YAML_DIR = Path(__file__).parent.parent / "machines"


def load_machine(filename: str) -> SingleTapeTM:
    return SingleTapeTM.from_yaml(YAML_DIR / filename)


def test_unary_to_binary_outputs() -> None:
    tm = load_machine("unary_to_binary.yaml")

    cases = [
        ("", ""),
        ("1", "1"),
        ("11", "10"),
        ("111", "11"),
        ("1111", "100"),
        ("11111", "101"),
    ]

    for input_string, expected in cases:
        result = tm.run(input_string, max_steps=10000)
        assert result.accepted is True
        assert result.final_tape == expected


def test_unary_to_binary_rejects_invalid_symbols() -> None:
    tm = load_machine("unary_to_binary.yaml")

    with pytest.raises(ValueError):
        tm.run("101")


def test_binary_compare_accepts_when_first_is_greater() -> None:
    tm = load_machine("binary_compare.yaml")

    for input_string in ["1#0", "10#1", "100#11", "1101#1100", "111#011"]:
        result = tm.run(input_string, max_steps=20000)
        assert result.accepted is True
        assert result.reason == "accept"


def test_binary_compare_rejects_when_first_is_not_greater() -> None:
    tm = load_machine("binary_compare.yaml")

    for input_string in ["0#0", "0#1", "1#1", "1011#1100", "11#100"]:
        result = tm.run(input_string, max_steps=20000)
        assert result.accepted is False
        assert result.reason == "reject"


def test_string_copy_outputs() -> None:
    tm = load_machine("string_copy.yaml")

    cases = [
        ("", "#"),
        ("a", "a#a"),
        ("b", "b#b"),
        ("ab", "ab#ab"),
        ("abba", "abba#abba"),
        ("baab", "baab#baab"),
    ]

    for input_string, expected in cases:
        result = tm.run(input_string, max_steps=20000)
        assert result.accepted is True
        assert result.final_tape == expected


def test_string_copy_rejects_invalid_symbols() -> None:
    tm = load_machine("string_copy.yaml")

    with pytest.raises(ValueError):
        tm.run("abc")


def test_student_choice_binary_divisible_by_4() -> None:
    tm = load_machine("student_choice.yaml")

    accepted = ["0", "100", "1000", "1100", "10100"]
    rejected = ["", "1", "10", "101", "1111"]

    for input_string in accepted:
        result = tm.run(input_string)
        assert result.accepted is True
        assert result.reason == "accept"

    for input_string in rejected:
        result = tm.run(input_string)
        assert result.accepted is False
        assert result.reason == "reject"
