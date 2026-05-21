"""
Bonus A: çok şeritli motor + a^n b^n c^n testleri.
"""

from pathlib import Path

import pytest
import yaml

from turinglab import MultiTapeTM


YAML_DIR = Path(__file__).parent.parent / "machines"


@pytest.fixture
def anbncn_tm() -> MultiTapeTM:
    return MultiTapeTM.from_yaml(YAML_DIR / "anbncn.yaml")


# YAML ve doğrulama testleri

def test_yaml_loads(anbncn_tm: MultiTapeTM) -> None:
    assert anbncn_tm.name == "anbncn"
    assert anbncn_tm.num_tapes == 3
    assert anbncn_tm.blank == "B"


def test_yaml_missing_num_tapes(tmp_path: Path) -> None:
    bad = {
        "states": ["q0"], "input_alphabet": ["a"], "tape_alphabet": ["a", "B"],
        "blank": "B", "start_state": "q0", "accept_states": [], "transitions": [],
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.dump(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="num_tapes"):
        MultiTapeTM.from_yaml(path)


def test_read_list_length_must_match(tmp_path: Path) -> None:
    """num_tapes=2 dedik ama read 3 uzunluğunda olursa hata vermeli."""
    bad = {
        "num_tapes": 2,
        "states": ["q0"], "input_alphabet": ["a"], "tape_alphabet": ["a", "B"],
        "blank": "B", "start_state": "q0", "accept_states": [],
        "transitions": [
            {"state": "q0", "read": ["a", "B", "B"], "next": "q0",
             "write": ["a", "B", "B"], "move": ["R", "R", "R"]},
        ],
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.dump(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="uzunlukta olmalı"):
        MultiTapeTM.from_yaml(path)


# a^n b^n c^n davranış testleri

def test_anbncn_accepts(anbncn_tm: MultiTapeTM) -> None:
    """L = {a^n b^n c^n} elemanları kabul edilmeli."""
    for n in [0, 1, 2, 3, 5]:
        s = "a" * n + "b" * n + "c" * n
        result = anbncn_tm.run(s, max_steps=5000)
        assert result.accepted is True, f"n={n} ({s!r}) kabul edilmeliydi"
        assert result.reason == "accept"


def test_anbncn_rejects_uneven_counts(anbncn_tm: MultiTapeTM) -> None:
    """Sayılar eşit olmayan durumlar reddedilmeli."""
    for s in ["aabbc", "aabbcccc", "aaabbcc", "abbc", "aabbbcc"]:
        result = anbncn_tm.run(s, max_steps=5000)
        assert result.accepted is False, f"{s!r} reddedilmeliydi"


def test_anbncn_rejects_wrong_order(anbncn_tm: MultiTapeTM) -> None:
    """a-b-c sırası bozuksa reddedilmeli."""
    for s in ["ba", "cab", "abcabc", "acb", "bac"]:
        result = anbncn_tm.run(s, max_steps=5000)
        assert result.accepted is False, f"{s!r} reddedilmeliydi"


def test_anbncn_invalid_symbol_raises(anbncn_tm: MultiTapeTM) -> None:
    """Girdi alfabesinde olmayan sembol ValueError vermeli."""
    with pytest.raises(ValueError):
        anbncn_tm.run("abx")


def test_final_tapes_is_list(anbncn_tm: MultiTapeTM) -> None:
    """final_tapes her şerit için bir string içermeli."""
    result = anbncn_tm.run("abc", max_steps=5000)
    assert isinstance(result.final_tapes, list)
    assert len(result.final_tapes) == 3


def test_history_grows_each_step(anbncn_tm: MultiTapeTM) -> None:
    result = anbncn_tm.run("aabbcc", max_steps=5000)
    assert len(result.history) == result.steps + 1
