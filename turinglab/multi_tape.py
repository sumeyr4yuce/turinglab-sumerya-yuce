"""
TuringLab -> Bonus A: Çok şeritli (multi-tape) TM

SingleTapeTM ile aynı mantık çalışıyor, sadece her geçiş kuralı
artık k şerit için ayrı ayrı (read, write, move) listesi alıyor.
Sadece tape 1 girdiyle başlıyor, diğer şeritler blank.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from .tm_engine import Tape


@dataclass(frozen=True)
class MultiTransition:
    """k-şeritli tek bir delta geçiş kuralı."""

    next_state: str
    writes: tuple[str, ...]
    moves: tuple[str, ...]   # L, R veya S (stay)

    def __post_init__(self) -> None:
        for m in self.moves:
            if m not in ("L", "R", "S"):
                raise ValueError(
                    f"Hareket yönü '{m}' hatalı! Sadece L, R veya S olabilir."
                )


@dataclass
class MultiRunResult:
    """Çok şeritli koşum sonucu. final_tapes her şerit için ayrı string."""

    accepted: bool
    reason: str
    final_tapes: list[str]
    steps: int
    history: list[tuple[str, list[str], list[int]]] = field(default_factory=list)


class MultiTapeTM:
    def __init__(
        self,
        name,
        num_tapes,
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
        self.num_tapes = num_tapes
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
        if self.num_tapes < 1:
            raise ValueError("num_tapes en az 1 olmalı!")
        if self.start_state not in self.states:
            raise ValueError(f"Başlangıç durumu '{self.start_state}' geçersiz!")
        if self.blank not in self.tape_alphabet:
            raise ValueError(f"Blank sembolü '{self.blank}' alfabede yok!")
        for s in self.accept_states:
            if s not in self.states:
                raise ValueError(f"Kabul durumu '{s}' tanımsız!")
        for s in self.reject_states:
            if s not in self.states:
                raise ValueError(f"Ret durumu '{s}' tanımsız!")
        for sym in self.input_alphabet:
            if sym not in self.tape_alphabet:
                raise ValueError(
                    f"Girdi alfabesindeki '{sym}' şerit alfabesinde yok!"
                )
        for (state, reads), trans in self.transitions.items():
            if len(reads) != self.num_tapes:
                raise ValueError(
                    f"Geçiş read listesi {self.num_tapes} uzunlukta olmalı, "
                    f"{len(reads)} verildi: ({state}, {reads})"
                )
            if len(trans.writes) != self.num_tapes:
                raise ValueError(
                    f"Geçiş write listesi {self.num_tapes} uzunlukta olmalı."
                )
            if len(trans.moves) != self.num_tapes:
                raise ValueError(
                    f"Geçiş move listesi {self.num_tapes} uzunlukta olmalı."
                )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "MultiTapeTM":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML dosyası bulunamadı: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(f"YAML ayrıştırma hatası ({path}): {exc}") from exc

        required_keys = [
            "num_tapes", "states", "input_alphabet", "tape_alphabet",
            "blank", "start_state", "accept_states", "transitions",
        ]
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise ValueError(f"YAML'da eksik alanlar: {missing}")

        trans_map: dict[tuple[str, tuple[str, ...]], MultiTransition] = {}
        for r in data["transitions"]:
            key = (str(r["state"]), tuple(str(x) for x in r["read"]))
            if key in trans_map:
                raise ValueError(
                    f"Deterministik TM için aynı (durum, semboller) iki kez "
                    f"tanımlı: {key}"
                )
            trans_map[key] = MultiTransition(
                next_state=str(r["next"]),
                writes=tuple(str(x) for x in r["write"]),
                moves=tuple(str(x).upper() for x in r["move"]),
            )

        return cls(
            name=data.get("name", "MTM"),
            num_tapes=int(data["num_tapes"]),
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
        self, input_string: str, max_steps: int = 20000, verbose: bool = False
    ) -> MultiRunResult:
        for ch in input_string:
            if ch not in self.input_alphabet:
                raise ValueError(f"'{ch}' sembolü girdi alfabesinde yok!")

        # Sadece tape 1 girdiyle başlar
        tapes = [Tape(input_string, self.blank)]
        for _ in range(self.num_tapes - 1):
            tapes.append(Tape("", self.blank))
        heads = [0] * self.num_tapes
        state = self.start_state
        steps = 0
        history: list[tuple[str, list[str], list[int]]] = []

        def snapshot():
            return (state, [t.to_string(h) for t, h in zip(tapes, heads)], list(heads))

        history.append(snapshot())

        while steps < max_steps:
            if state in self.accept_states:
                if verbose:
                    self._print_step(steps, state, tapes, heads, None)
                break
            if state in self.reject_states:
                if verbose:
                    self._print_step(steps, state, tapes, heads, None)
                break

            reads = tuple(t.read(h) for t, h in zip(tapes, heads))
            rule = self.transitions.get((state, reads))

            if not rule:
                if verbose:
                    self._print_step(steps, state, tapes, heads, None)
                return MultiRunResult(
                    False,
                    "no_transition",
                    [t.to_string(h).strip(self.blank) for t, h in zip(tapes, heads)],
                    steps,
                    history,
                )

            if verbose:
                self._print_step(steps, state, tapes, heads, rule.moves)

            for i in range(self.num_tapes):
                tapes[i].write(heads[i], rule.writes[i])
            state = rule.next_state
            for i in range(self.num_tapes):
                if rule.moves[i] == "R":
                    heads[i] += 1
                elif rule.moves[i] == "L":
                    heads[i] -= 1
                # S: yerinde dur
            steps += 1

            history.append(snapshot())

        is_accepted = state in self.accept_states
        if is_accepted:
            reason = "accept"
        elif steps >= max_steps:
            reason = "timeout"
        else:
            reason = "reject"

        return MultiRunResult(
            is_accepted,
            reason,
            [t.to_string(h).strip(self.blank) for t, h in zip(tapes, heads)],
            steps,
            history,
        )

    def _print_step(self, step, state, tapes, heads, moves) -> None:
        parts = [f"Adım {step}", f"Durum: {state}"]
        for i, (t, h) in enumerate(zip(tapes, heads)):
            parts.append(f"Şerit{i + 1}: {t.to_string_with_head(h)}")
        if moves:
            parts.append(f"Hareket: {','.join(moves)}")
        print(" | ".join(parts))
