# -*- coding: utf-8 -*-
"""verify.py — проверка строк поиска (find) в tools/data/actNNN.py против исходных статей.

Использование: python3 tools/verify.py 169 [170 ...]
Для каждого repl-кортежа сообщает: OK / НЕ НАЙДЕН, а при расхождении — точку расхождения и контекст.
"""
import sys, importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "data"))
from build_act import split_articles, clean, find_span  # noqa: E402


def longest_prefix(needle, hay):
    lo, hi = 0, len(needle)
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if needle[:mid] in hay:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


for arg in sys.argv[1:]:
    num = int(arg)
    mod = importlib.import_module(f"act{num}")
    arts = {}
    for n, b in split_articles(num):
        arts[n] = clean(b)
    print(f"=== {num} ===")
    bad = 0
    for i, row in enumerate(mod.DOC["rows"]):
        if not row["src"]:
            continue
        an = str(row["src"][1])
        txt = arts.get(an)
        if txt is None:
            print(f"  [строка {i}] НЕТ СТАТЬИ {an}")
            bad += 1
            continue
        for j, (f, p) in enumerate(row.get("repl") or []):
            if f in txt or find_span(txt, f) is not None:
                continue
            bad += 1
            k = longest_prefix(f, txt)
            print(f"  [строка {i} ст.{an} repl#{j}] НЕ НАЙДЕН (совпало {k}/{len(f)})")
            print(f"      src ctx: {txt[max(0,k-60):k+60]!r}")
            print(f"      find ctx:{f[max(0,k-60):k+60]!r}")
    print("  ВСЁ ОК" if not bad else f"  ПРОБЛЕМ: {bad}")
