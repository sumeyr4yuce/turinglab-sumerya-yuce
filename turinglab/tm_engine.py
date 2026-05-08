"""
TuringLab -> Bölüm 1: TM Motoru
bu dosya YAML dosyasından okunan kurallara göre çalışan
deterministik tek şeritli bir Turing makinesi simülatörüdür.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass(frozen=True)
class Configuration:
    """Bir adımdaki anlık makine konfigürasyonu.

    Attributes:
        state: O andaki durum adı.
        tape: Şeridin görüntüsü (string).
        head_position: Kafanın indeksi.
    """

    state: str
    tape: str
    head_position: int


@dataclass
class RunResult:
    """
    accepted: kabul mü?
    reason: neden durdu? (accept, timeout, no_transition vb.)
    """

    accepted: bool
    reason: str
    final_tape: str
    steps: int
    history: list[Configuration] = field(default_factory=list)


@dataclass(frozen=True)
class Transition:
    """Tek bir delta geçiş kuralı."""

    next_state: str
    write: str
    move: str  # L veya R

    def __post_init__(self) -> None:
        # Hatalı YAML girişlerini önlemek için kontrol
        if self.move not in ("L", "R"):
            raise ValueError(
                f"Hareket yönü '{self.move}' hatalı! Sadece L veya R olabilir."
            )


class Tape:
    """Sonsuz şerit mantığını dict kullanarak kurdum. Liste kullansaydım kafa negatif
    indeks'e (sola) gittiğinde Python listenin sonuna atlıyordu.
    Dict ile kafa her yere gidebiliyor.
    """

    def __init__(self, input_string: str, blank: str = "B") -> None:
        self.blank = blank
        # İndeks bazlı erişim için sözlük yapısı (sparse tape).
        self._cells: dict[int, str] = {i: ch for i, ch in enumerate(input_string)}

    def read(self, position: int) -> str:
        """Verilen pozisyondaki sembolü okur; hücre yoksa blank döner."""
        return self._cells.get(position, self.blank)

    def write(self, position: int, symbol: str) -> None:
        """Verilen pozisyona sembol yazar; blank yazılırsa hücreyi siler."""
        if symbol == self.blank:
            self._cells.pop(position, None)
        else:
            self._cells[position] = symbol

    def to_string(self, head: int, padding: int = 1) -> str:
        """Şeridi okunabilir string'e çevir."""
        if not self._cells and head == 0:
            return self.blank
        all_pos = list(self._cells.keys()) + [head]
        lo, hi = min(all_pos) - padding, max(all_pos) + padding
        return "".join(self.read(i) for i in range(lo, hi + 1))

    def to_string_with_head(self, head: int) -> str:
        """Kafa konumu köşeli parantez içinde gösterilir. Örnek: 10[1]1B"""
        all_pos = list(self._cells.keys()) + [head]
        lo, hi = min(all_pos) - 1, max(all_pos) + 1
        res = []
        for i in range(lo, hi + 1):
            char = self.read(i)
            res.append(f"[{char}]" if i == head else char)
        return "".join(res)


# ANA MOTOR

class SingleTapeTM:
    def __init__(
        self,
        name,
        states,
        input_alphabet,
        tape_alphabet,
        blank,
        start_state,
        accept_states,
        reject_states,
        transitions,
    ):
        self.name = name
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.blank = blank
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.transitions = transitions
        self._validate()

    def _validate(self) -> None:
        """Tanımların tutarlılığını kontrol eden kısım."""
        for s in self.accept_states:
            if s not in self.states:
                raise ValueError(f"Kabul durumu '{s}' durumlar kümesinde yok!")
        if self.blank not in self.tape_alphabet:
            raise ValueError(f"Blank sembolü '{self.blank}' alfabede yok!")
        if self.start_state not in self.states:
            raise ValueError(f"Başlangıç durumu '{self.start_state}' geçersiz!")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "SingleTapeTM":
        """El kitabındaki YAML formatına uygun yükleme yapar."""
        path = Path(path)

        # Dosya varlık kontrolü try bloğundan ÖNCE yapılmalı.
        if not path.exists():
            raise FileNotFoundError(f"YAML dosyası bulunamadı: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(f"YAML ayrıştırma hatası ({path}): {exc}") from exc

        # El kitabındaki zorunlu alanlar tam mı?
        required_keys = [
            "states", "input_alphabet", "tape_alphabet",
            "blank", "start_state", "accept_states", "transitions",
        ]
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise ValueError(f"YAML dosyasında şu zorunlu alanlar eksik: {missing}")

        #Geçiş kurallarını (state, read) -> Transition şeklinde sözlüğe çevir.
        trans_map = {}
        for r in data["transitions"]:
            key = (str(r["state"]), str(r["read"]))
            trans_map[key] = Transition(
                str(r["next"]), str(r["write"]), str(r["move"]).upper()
            )

        return cls(
            name=data.get("name", "TM"),
            states=set(data["states"]),
            input_alphabet=set(data["input_alphabet"]),
            tape_alphabet=set(data["tape_alphabet"]),
            blank=str(data["blank"]),
            start_state=str(data["start_state"]),
            accept_states=set(data["accept_states"]),
            reject_states=set(data.get("reject_states", [])),
            transitions=trans_map,
        )

    def run(
        self, input_string: str, max_steps: int = 10000, verbose: bool = False
    ) -> RunResult:
        """Turing Makinesini adım adım çalıştıran ana fonksiyon."""
        for ch in input_string:
            if ch not in self.input_alphabet:
                raise ValueError(f"'{ch}' sembolü girdi alfabesinde yok!")

        tape = Tape(input_string, self.blank)
        state = self.start_state
        head, steps = 0, 0
        history = []

        #Başlangıç halini kaydet
        history.append(Configuration(state, tape.to_string(head), head))
        if verbose:
            print(f"Adım 0 | Durum: {state} | Şerit: {tape.to_string_with_head(head)}")

        while steps < max_steps:
            if state in self.accept_states:
                break
            if state in self.reject_states:
                break

            symbol = tape.read(head)
            rule = self.transitions.get((state, symbol))

            if not rule:
                return RunResult(
                    False,
                    "no_transition",
                    tape.to_string(head).strip(self.blank),
                    steps,
                    history,
                )

            tape.write(head, rule.write)
            state = rule.next_state
            head += 1 if rule.move == "R" else -1
            steps += 1

            history.append(Configuration(state, tape.to_string(head), head))
            if verbose:
                print(
                    f"Adım {steps} | Durum: {state} | "
                    f"Şerit: {tape.to_string_with_head(head)} | Hareket: {rule.move}"
                )

        is_accepted = state in self.accept_states
        reason = (
            "accept" if is_accepted else ("timeout" if steps >= max_steps else "reject")
        )

        return RunResult(
            is_accepted,
            reason,
            tape.to_string(head).strip(self.blank),
            steps,
            history,
        )
