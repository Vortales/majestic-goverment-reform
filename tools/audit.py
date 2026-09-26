#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit.py — жёсткая проверка всех ACT/*.docx: форма Приложения № 2, две колонки,
правильные заголовки, соответствие номера в заголовке имени файла, наличие
красной/зелёной подсветки в каждой содержательной строке."""
import sys, os, re, glob
from docx import Document
from docx.shared import RGBColor

RED = RGBColor(0xC0, 0, 0)
GREEN = RGBColor(0, 0x7A, 0)

HEAD = [
    "IN THE SENATE OF THE STATE OF SAN ANDREAS",
    "MARCH 00, 2026",
    "ЗАКОНОПРОЕКТ",
    "о внесении изменений в действующий закон",
    "SECTION 1. СУТЬ ПРАВКИ",
    "SECTION 2. ВНЕСЕНИЕ ПРАВКИ В",
]
COLS = ["настоящая редакция", "предложенный вариант"]

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def audit(path):
    issues = []
    d = Document(path)
    num = re.search(r"(\d{3})", os.path.basename(path)).group(1)
    paras = [norm(p.text) for p in d.paragraphs]
    title = paras[0] if paras else ""
    if title != f"ACT. {num}":
        issues.append(f"заголовок «{title}» ≠ «ACT. {num}»")
    joined = " \n ".join(paras)
    for h in HEAD:
        if h not in joined:
            issues.append(f"нет обязательной строки «{h}»")
    m = re.search(r"SECTION 2\. ВНЕСЕНИЕ ПРАВКИ В\s*(.+)", joined)
    if m and len(m.group(1).strip()) < 10:
        issues.append("SECTION 2 без полного наименования закона")
    tabs = d.tables
    if len(tabs) != 1:
        issues.append(f"таблиц: {len(tabs)} (ожидается 1)")
        return issues
    t = tabs[0]
    if len(t.columns) != 2:
        issues.append(f"колонок: {len(t.columns)} (ожидается 2)")
    hdr = [norm(c.text).lower() for c in t.rows[0].cells]
    if hdr != COLS:
        issues.append(f"заголовок таблицы: {hdr} ≠ {COLS}")
    if len(t.rows) < 2:
        issues.append("в таблице нет строк сравнения")
    for ri, row in enumerate(t.rows[1:], start=1):
        c0, c1 = row.cells[0], row.cells[1]
        red = green = 0
        for p in c0.paragraphs:
            for r in p.runs:
                if r.font.color and r.font.color.rgb == RED:
                    red += len(r.text)
        for p in c1.paragraphs:
            for r in p.runs:
                if r.font.color and r.font.color.rgb == GREEN:
                    green += len(r.text)
        if not norm(c0.text) or not norm(c1.text):
            issues.append(f"строка {ri}: пустая ячейка")
        if red == 0 and green == 0:
            issues.append(f"строка {ri}: нет ни красной, ни зелёной подсветки")
        # длина «настоящей редакции» не должна превышать «предложенную» более чем вдвое
        # (признак усечения нового текста)
        if len(norm(c1.text)) < len(norm(c0.text)) * 0.34:
            issues.append(f"строка {ri}: предложенный вариант подозрительно короче настоящего "
                          f"({len(norm(c1.text))} против {len(norm(c0.text))})")
    return issues

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("ACT/ACT.*.docx"))
    total = 0
    for f in files:
        if not f.endswith(".docx"):
            f = f"ACT/ACT.{f}.docx"
        iss = audit(f)
        total += len(iss)
        print(f"### {os.path.basename(f)}: {'OK' if not iss else str(len(iss)) + ' замечаний'}")
        for i in iss[:15]:
            print("   -", i)
    print(f"\nИТОГО замечаний: {total} (проверено файлов: {len(files)})")
