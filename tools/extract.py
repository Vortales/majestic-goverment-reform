#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Утилита: печать полной статьи из файла пакета 144-174."""
import re, sys, os, unicodedata

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "Предлагаемое на сенат законодательство")

ZW = "\u200b"

def load(act):
    p = os.path.join(BASE, f"{act}.txt")
    t = open(p, encoding="utf-8-sig").read()
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t

def split_articles(act):
    t = load(act)
    if act == 163:
        pat = re.compile(r"^\s*(\d+(?:\.\d+)+)\s", re.M)
    else:
        pat = re.compile(r"^\s*Статья\s+([0-9]+(?:\.[0-9]+)*)", re.M)
    ms = list(pat.finditer(t))
    out = []
    for i, m in enumerate(ms):
        end = ms[i+1].start() if i+1 < len(ms) else len(t)
        body = t[m.start():end]
        # обрезаем хвостовые главы/разделы? оставляем как есть
        out.append((m.group(1), body.strip()))
    return out

def show(act, arts=None, grep=None):
    for num, body in split_articles(act):
        if arts is not None and num not in arts:
            continue
        if grep is not None and grep.lower() not in body.lower():
            continue
        body = body.replace(ZW, "")
        print("="*100)
        print(body)
    print()

def numbers(act):
    nums = [n for n, _ in split_articles(act)]
    print(f"ACT {act}: {len(nums)} articles")
    print(", ".join(nums))

if __name__ == "__main__":
    act = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "list":
        numbers(act)
    elif len(sys.argv) > 2 and sys.argv[2].startswith("/"):
        show(act, grep=sys.argv[2][1:])
    else:
        arts = set(sys.argv[2:])
        show(act, arts)
