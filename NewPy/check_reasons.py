#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сверяет количество обоснований с количеством статей в спеках."""
import sys, os
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
for p in (R1, R2, R3, R4):
    REASONS.update(p)

specs = SPECS_A + SPECS_B + SPECS_C + SPECS_D + SPECS_E
tot_a = tot_r = 0
bad = False
for s in specs:
    n = s["num"]
    na = len(s["articles"])
    block = REASONS.get(n)
    nr = len(block["items"]) if block else 0
    tot_a += na; tot_r += nr
    flag = "" if na == nr else "  <<< MISMATCH"
    if na != nr:
        bad = True
    print(f"ACT {n}: статей {na}, обоснований {nr}{flag}")
print(f"ИТОГО: статей {tot_a}, обностей {tot_r}")
missing = [s["num"] for s in specs if s["num"] not in REASONS]
extra = [k for k in REASONS if k not in [s["num"] for s in specs]]
if missing: print("нет данных:", missing); bad = True
if extra: print("лишние акты:", extra); bad = True
sys.exit(1 if bad else 0)
