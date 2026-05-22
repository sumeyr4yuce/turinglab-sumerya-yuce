"""
TuringLab - Test Dosyası
Bu dosya motorun doğru çalışıp çalışmadığını denetleyen 'pytest' testlerini içerir. 10 farklı test fonksiyonu ile YAML yükleme, çalıştırma sonuçları, kenar durumlar ve hata yönetimi gibi çeşitli senaryoları kapsar.
"""

import pytest
import yaml
from pathlib import Path
from turinglab.tm_engine import Configuration, RunResult, SingleTapeTM, Tape

YAML_DIR = Path(__file__).parent.parent / "machines"

@pytest.fixture
def binary_increment_tm() -> SingleTapeTM:
    """Hocanın verdiği binary_increment örneğini testlerde kullanmak
    için yüklüyoruz."""
    return SingleTapeTM.from_yaml(YAML_DIR / "binary_increment.yaml")

#YAML YÜKLEME TESTLERİ

def test_yaml_loads_correctly(binary_increment_tm: SingleTapeTM) -> None:
    """Dosya doğru yüklendiğinde içindeki isim, durumlar ve blank sembolü doğru mu?"""
    tm = binary_increment_tm
    assert tm.name == "binary_increment"
    assert "q0" in tm.states
    assert tm.blank == "B"

def test_yaml_invalid_raises_value_error(tmp_path: Path) -> None:
    """eğer YAML bozuksa (parantez açık kalmışsa vb.) ValueError vermeli."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("states: [q0\n  - unclosed", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML ayrıştırma hatası"):
        SingleTapeTM.from_yaml(bad_yaml)

def test_yaml_missing_field_raises_value_error(tmp_path: Path) -> None:
    """YAML'da zorunlu bir alan eksikse motor hata vermeli."""
    incomplete = {"states": ["q0", "q_accept"], "blank": "B"} # Eksik bilgi
    bad_yaml = tmp_path / "incomplete.yaml"
    bad_yaml.write_text(yaml.dump(incomplete), encoding="utf-8")
    with pytest.raises(ValueError):
        SingleTapeTM.from_yaml(bad_yaml)

# ÇALIŞTIRMA TESTLERİ

def test_run_returns_run_result(binary_increment_tm: SingleTapeTM) -> None:
    """Motorun run fonksiyonu her zaman RunResult tipinde bir sonuç dönmeli."""
    result = binary_increment_tm.run("0", max_steps=100)
    assert isinstance(result, RunResult)

def test_binary_increment_outputs(binary_increment_tm: SingleTapeTM) -> None:
    """El kitabındaki binary_increment örneğindeki 1011 -> 1100 dönüşümünü deneme."""

    # Sayfa 8 'Test Kapsamı': her TM için 5+ girdi.
    test_cases = [
        ("0", "1"),
        ("1", "10"),
        ("10", "11"),
        ("111", "1000"),
        ("1011", "1100"),
    ]
    for inp, expected in test_cases:
        result = binary_increment_tm.run(inp)
        assert result.accepted is True
        assert result.final_tape == expected


def test_unary_to_binary_outputs_engine() -> None:
    """Motoru ikinci bir TM (unary->binary) ile de doğrula (Sayfa 8 kuralı)."""
    tm = SingleTapeTM.from_yaml(YAML_DIR / "unary_to_binary.yaml")
    cases = [
        ("", ""),
        ("1", "1"),
        ("11", "10"),
        ("111", "11"),
        ("11111", "101"),
    ]
    for inp, expected in cases:
        result = tm.run(inp, max_steps=10000)
        assert result.accepted is True
        assert result.final_tape == expected


def test_student_choice_outputs_engine() -> None:
    """Üçüncü TM (4'e bölünebilirlik) ile motorun doğru çalıştığını doğrula."""
    tm = SingleTapeTM.from_yaml(YAML_DIR / "student_choice.yaml")
    accepted = ["0", "100", "1000", "1100", "10000"]
    rejected = ["", "1", "10", "11", "101"]
    for inp in accepted:
        result = tm.run(inp)
        assert result.accepted is True
        assert result.reason == "accept"
    for inp in rejected:
        result = tm.run(inp)
        assert result.accepted is False
        assert result.reason == "reject"

#KENAR DURUMLAR VE HATA YÖNETİMİ

def test_history_integrity(binary_increment_tm: SingleTapeTM) -> None:
    """History uzunluğu(başlangıç durumuyla birlikte) adım sayısından 1 fazla olmalı."""
    result = binary_increment_tm.run("1011")
    # El kitabındaki 23 adım / 24 history örneğine göre kontrol:
    assert len(result.history) == result.steps + 1

def test_timeout_status(tmp_path: Path) -> None:
    """Sonsuz döngüye giren bir makine max_steps dolunca 'timeout' ile durmalı."""
    loop_yaml = tmp_path / "loop.yaml"
    # Sürekli sağa giden basit bir döngü:
    loop_def = {
        "states": ["q0"], "input_alphabet": ["0"], "tape_alphabet": ["0", "B"],
        "blank": "B", "start_state": "q0", "accept_states": [], "transitions": [
            {"state": "q0", "read": "0", "next": "q0", "write": "0", "move": "R"},
            {"state": "q0", "read": "B", "next": "q0", "write": "B", "move": "R"}
        ]
    }
    loop_yaml.write_text(yaml.dump(loop_def))
    tm = SingleTapeTM.from_yaml(loop_yaml)
    result = tm.run("00", max_steps=10)
    assert result.reason == "timeout"

def test_no_transition_status(tmp_path: Path) -> None:
    """Eğer şeritteki sembol için hiçbir kural yoksa 'no_transition' demeli."""
    dead_end_def = {
        "states": ["q0"], "input_alphabet": ["0"], "tape_alphabet": ["0", "B"],
        "blank": "B", "start_state": "q0", "accept_states": [], "transitions": []
    }
    path = tmp_path / "dead.yaml"
    path.write_text(yaml.dump(dead_end_def))
    tm = SingleTapeTM.from_yaml(path)
    result = tm.run("0")
    assert result.reason == "no_transition"

def test_verbose_format(binary_increment_tm: SingleTapeTM, capsys) -> None:
    """Verbose modunda adım ve şerit formatının el kitabındaki gibi olup olmadığını kontrol eder."""
    binary_increment_tm.run("1", verbose=True)
    captured = capsys.readouterr()
    assert "Adım" in captured.out
    assert "Şerit" in captured.out

def test_head_pos_is_int(binary_increment_tm: SingleTapeTM) -> None:
    """head_position history içinde her zaman int olmalı."""
    result = binary_increment_tm.run("1")
    for cfg in result.history:
        assert isinstance(cfg.head_position, int)
