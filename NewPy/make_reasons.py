#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерирует NewPy/<NNN>.md — обоснование правок к каждому ACT. NNN.

Заголовок каждой статьи выводится из текста статьи в спеке:
  - текущая первая строка начинается со «Статья»/«Пункт»/числа — берётся она;
  - иначе (статья отсутствует/восстановлена) — первая строка предлагаемого варианта.
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from content_A import SPECS_A
from content_B import SPECS_B
from content_C import SPECS_C
from content_D import SPECS_D
from content_E import SPECS_E
from reasons_data1 import REASONS as R1
from reasons_data2 import REASONS as R2
from reasons_data3 import REASONS as R3
from reasons_data4 import REASONS as R4

REASONS = {}
for part in (R1, R2, R3, R4):
    REASONS.update(part)

SPECS = SPECS_A + SPECS_B + SPECS_C + SPECS_D + SPECS_E

MARK = re.compile(r"\[\[|\]\]|\{\{|\}\}|\*\*")
NUM = re.compile(r"^(\d+(?:\.\d+)+)")
HEADS = ("Статья", "Статья", "ГЛАВА", "Глава", "Пункт", "Раздел")


def clean(s):
    return MARK.sub("", s).strip()


def first_line(text):
    for line in text.splitlines():
        c = clean(line)
        if c:
            return c
    return ""


def truncate(title, limit=110):
    if len(title) <= limit:
        return title
    cut = title[:limit]
    sp = cut.rfind(" ")
    if sp > 40:
        cut = cut[:sp]
    return cut.rstrip(",;:.") + "…"


def derive_title(art):
    cur = first_line(art["current"])
    prop = first_line(art["proposed"])
    for src in (cur, prop):
        if src.startswith("Пункт "):
            m = re.match(r"Пункт (\d+(?:\.\d+)+)", src)
            if m:
                title = "Пункт " + m.group(1)
                if "утратил силу" in src[:40]:
                    title += " (утратил силу)"
                return title
        if src.startswith(HEADS):
            return truncate(src)
    for src in (cur, prop):
        m = NUM.match(src)
        if m:
            return truncate("Пункт " + m.group(1))
    if cur.startswith("(") and prop:
        return truncate(prop)
    return truncate(cur or prop)


def main():
    problems = []
    written = 0
    total = 0
    for spec in SPECS:
        num = spec["num"]
        law = spec["law"]
        arts = spec["articles"]
        block = REASONS.get(num)
        if block is None:
            problems.append("ACT %d: нет данных обоснований" % num)
            continue
        items = block["items"]
        if len(items) != len(arts):
            problems.append(
                "ACT %d: %d обоснований против %d статей"
                % (num, len(items), len(arts))
            )
            continue
        lines = ["# Обоснование к ACT. %d — %s" % (num, law), ""]
        lines.append(block["intro"])
        lines.append("")
        for art, item in zip(arts, items):
            title, pravka, obosn = item
            if not title:
                title = derive_title(art)
            lines.append("## %s" % title)
            lines.append("")
            lines.append("**Правка:** %s" % pravka)
            lines.append("")
            lines.append("**Почему нужно:** %s" % obosn)
            lines.append("")
            total += 1
        out = os.path.join(BASE, "%d.md" % num)
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")
        written += 1
        print("OK  %d.md  (%d статей)" % (num, len(arts)))
    print("ИТОГО: актов %d/30, статей обосновано %d/139" % (written, total))
    if problems or written != 30 or total != 139:
        for p in problems:
            print("ПРОБЛЕМА:", p)
        sys.exit(1)
    print("ВСЁ КОРРЕКТНО")


if __name__ == "__main__":
    main()
