#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка документов ACT.<номер>.docx из модулей tools/data/actNNN.py"""
import sys, os, importlib, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "data"))
import build_act as B

def build_one(num):
    mod = importlib.import_module(f"act{num}")
    importlib.reload(mod)
    return B.build(mod.DOC)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["all"]:
        files = sorted(glob.glob(os.path.join(HERE, "data", "act*.py")))
        args = [re.search(r"act(\d+)\.py", f).group(1) for f in files]
    for a in args:
        try:
            p = build_one(int(a))
            print("OK  ", p)
        except Exception as e:
            print("FAIL", a, "->", type(e).__name__, e)
            raise
