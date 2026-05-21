"""
Bonus C: Aynı dili (L = {a^n b^n}) tek şeritli ve iki şeritli TM ile çözüp
adım sayılarını karşılaştırır.

Çalıştırma:
    python scripts/compare_anbn.py

Çıktı: docs/comparison.png
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

from turinglab import MultiTapeTM, SingleTapeTM

MACHINES = ROOT / "machines"
OUT = ROOT / "docs" / "comparison.png"


def main() -> None:
    single = SingleTapeTM.from_yaml(MACHINES / "anbn_1tape.yaml")
    multi = MultiTapeTM.from_yaml(MACHINES / "anbn_2tape.yaml")

    ns = list(range(1, 21))
    single_steps = []
    multi_steps = []

    for n in ns:
        inp = "a" * n + "b" * n
        r1 = single.run(inp, max_steps=100000)
        r2 = multi.run(inp, max_steps=100000)
        assert r1.accepted, f"1-şerit n={n} kabul etmeliydi"
        assert r2.accepted, f"2-şerit n={n} kabul etmeliydi"
        single_steps.append(r1.steps)
        multi_steps.append(r2.steps)
        print(f"n={n:2d}  1-tape: {r1.steps:5d} adım   |   2-tape: {r2.steps:3d} adım")

    plt.figure(figsize=(8, 5))
    plt.plot(ns, single_steps, marker="o", label="Tek şeritli  (O(n^2))")
    plt.plot(ns, multi_steps, marker="s", label="İki şeritli   (O(n))")
    plt.xlabel("n  (girdi: a^n b^n)")
    plt.ylabel("Adım sayısı")
    plt.title("a^n b^n: tek şeritli vs iki şeritli TM")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    OUT.parent.mkdir(exist_ok=True)
    plt.savefig(OUT, dpi=120)
    print(f"\nGrafik yazıldı -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
