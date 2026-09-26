# -*- coding: utf-8 -*-
"""xref.py — проверка ссылок на статьи и главы кодексов внутри собранных ACT-документов.

Ищет строгие формы «статья/статьи/статьёй/статьями N … кодекса штата San-Andreas» и
«глава/главой N … кодекса» в предлагаемых редакциях и проверяет, что статья (глава) N
существует в исходном файле пакета либо вводится одним из актов.
Диапазоны вида «статьи 12.1 – 12.3» раскрываются.
"""
import re, sys, importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "data"))
from build_act import split_articles  # noqa: E402

CODEX = {
    "Уголовного": 144, "Процессуального": 145, "Административного": 146,
    "Дорожного": 147, "Трудового": 148, "Гражданского": 149, "Этического": 150,
}
CODEX_NAMES = "|".join(CODEX)
NUMS = [n for n in range(144, 175) if n != 151]

SRC = {num: split_articles(num) for num in CODEX.values()}
exists = {num: {n for n, b in SRC[num]} for num in CODEX.values()}
CHAPTERS = {num: set(re.findall(r"(?:ГЛАВА|Глава|глава)\s+\.?\s*(\d+)", "\n".join(b for n, b in SRC[num])))
            for num in CODEX.values()}

# статьи и главы, вводимые актами
added = {n: set() for n in NUMS}
for n in NUMS:
    doc = importlib.import_module(f"act{n}").DOC
    for row in doc["rows"]:
        blobs = [row.get("add") or "", row.get("new") or ""]
        blobs += [p for f, p in row.get("repl") or []]
        for b in blobs:
            for m in re.finditer(r"(?:Статья|статья)\s+(\d+(?:\.\d+)*)", b):
                added[n].add(m.group(1))
            for m in re.finditer(r"(?:^|\n)\s*(\d+\.\d+(?:\.\d+)?)\s", b):
                added[n].add(m.group(1))
            for m in re.finditer(r"[Гг]лав\w*\s+(\d+)", b):
                added[n].add("гл." + m.group(1))


def expand_range(a, b):
    """12.1 – 12.3 -> [12.2] (крайние значения уже перечислены явно)."""
    if "." not in a or "." not in b:
        return []
    ia, fa = a.split(".")
    ib, fb = b.split(".")
    if ia != ib or not (fa.isdigit() and fb.isdigit()):
        return []
    return [f"{ia}.{k}" for k in range(int(fa) + 1, int(fb))]


STRICT = re.compile(r"[Сс]тать\w*\s+((?:\d+(?:\.\d+)*(?:\s*(?:,|и|–|—|-)\s*)?)+)\s*("
                    + CODEX_NAMES + r")\s+кодекса")
CHAP = re.compile(r"[Гг]лав\w*\s+(\d+)\s*(" + CODEX_NAMES + r")\s+кодекса")

problems = checked = 0
for n in NUMS:
    doc = importlib.import_module(f"act{n}").DOC
    parts = []
    for row in doc["rows"]:
        parts.append(row.get("add") or "")
        parts.append(row.get("new") or "")
        parts += [p for f, p in row.get("repl") or []]
    text = "\n".join(parts)

    for m in STRICT.finditer(text):
        seg, codex_name = m.group(1), m.group(2)
        nums = re.findall(r"\d+(?:\.\d+)*", seg)
        for a, b in re.findall(r"(\d+\.\d+)\s*[–—-]\s*(\d+\.\d+)", seg):
            nums += expand_range(a, b)
        codex = CODEX[codex_name]
        for num in nums:
            checked += 1
            if num in exists[codex] or num in added[codex] or num in added[n]:
                continue
            problems += 1
            print(f"  ACT.{n}: ссылка на ст. {num} {codex_name} кодекса — не найдена "
                  f"(в исходнике {codex} её нет и правками она не вводится)")

    for m in CHAP.finditer(text):
        ch, codex_name = m.group(1), m.group(2)
        codex = CODEX[codex_name]
        checked += 1
        if ch in CHAPTERS[codex] or f"гл.{ch}" in added[codex] or f"гл.{ch}" in added[n]:
            continue
        problems += 1
        print(f"  ACT.{n}: ссылка на главу {ch} {codex_name} кодекса — не найдена")

print(f"Проверено ссылок: {checked}; проблем: {problems}")
