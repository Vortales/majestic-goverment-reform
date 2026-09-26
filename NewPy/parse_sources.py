# -*- coding: utf-8 -*-
"""Parse 'Предлагаемое на сенат законодательство/<act>.txt' into
/home/user/tools/articles/<act>.json consumed by content_A..E.

Segment kinds:
  article  — kind="article", key="1.9", text="Статья 1.9 Судимость\\nч. 1 ..."
  para     — kind="para",    key="1.1", text="1.1 ..."   (laws written as numbered puntos, e.g. 163)
  preamble — kind="preamble", text before the first article/punto
"""
import re
import json
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "Предлагаемое на сенат законодательство")
OUT = "/home/user/tools/articles"

ART_RE = re.compile(r"^Статья\s+(\d+(?:\.\d+)*)([*.:]?)\s*(.*)$")
PAR_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)*)\s+(.*)$")
STRUC_RE = re.compile(
    r"^(РАЗДЕЛ|ГЛАВА|ОТДЕЛ|ПРИЛОЖЕНИЕ|Раздел|Глава|Отдел|Приложение)\b"
)


def clean_lines(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for l in text.split("\n"):
        # remove zero-width characters only; KEEP ordinary leading/trailing
        # spaces — some mark() anchors in content_*.py include them
        l = l.replace("\u200b", "").replace("\ufeff", "")
        out.append(l if l.strip() else "")
    return out


def parse_article_style(lines):
    """Returns list of segments for a file whose body is made of 'Статья N ...' articles."""
    segs = []
    pre = []          # lines before first article
    cur = None        # (key, [lines])
    started = False   # first article already seen

    def close():
        nonlocal cur
        if cur is not None:
            key, ls = cur
            while ls and not ls[-1]:
                ls.pop()
            segs.append({"kind": "article", "key": key,
                         "text": re.sub(r"\n{3,}", "\n\n", "\n".join(ls))})
            cur = None

    for l in lines:
        m = ART_RE.match(l)
        if m:
            close()
            started = True
            key = m.group(1)
            # keep the header line as it appears (normalized: number + title)
            header = ("Статья " + key + (m.group(2) if m.group(2) else "")
                      + ((" " + m.group(3)) if m.group(3) else "")).rstrip()
            cur = (key, [header])
            continue
        if STRUC_RE.match(l):
            # structural heading ends the current article; in the preamble it is skipped
            close()
            continue
        if cur is not None:
            cur[1].append(l)
        elif not started:
            pre.append(l)
    close()
    if pre:
        while pre and not pre[-1]:
            pre.pop()
        if pre:
            segs.insert(0, {"kind": "preamble",
                            "text": re.sub(r"\n{3,}", "\n\n", "\n".join(pre))})
    return segs


def parse_para_style(lines):
    """Returns segments for a file written as numbered puntos (e.g. 163)."""
    segs = []
    pre = []
    cur = None
    closed = False

    def close():
        nonlocal cur, closed
        if cur is not None:
            key, ls = cur
            while ls and not ls[-1]:
                ls.pop()
            segs.append({"kind": "para", "key": key,
                         "text": re.sub(r"\n{3,}", "\n\n", "\n".join(ls))})
            cur = None
        closed = True

    for l in lines:
        m = PAR_RE.match(l)
        if m:
            close()
            cur = (m.group(1), [l])
            continue
        if STRUC_RE.match(l):
            close()
            continue
        if cur is not None:
            cur[1].append(l)
        elif not closed:
            pre.append(l)
    close()
    if pre:
        while pre and not pre[-1]:
            pre.pop()
        if pre:
            segs.insert(0, {"kind": "preamble",
                            "text": re.sub(r"\n{3,}", "\n\n", "\n".join(pre))})
    return segs


def parse_file(path):
    lines = clean_lines(open(path, encoding="utf-8", errors="replace").read())
    n_art = sum(1 for l in lines if ART_RE.match(l))
    n_par = sum(1 for l in lines if PAR_RE.match(l) and not ART_RE.match(l))
    if n_art >= n_par:
        return {"segments": parse_article_style(lines)}
    return {"segments": parse_para_style(lines)}


def main(acts):
    os.makedirs(OUT, exist_ok=True)
    for act in acts:
        path = os.path.join(SRC, "%d.txt" % act)
        if not os.path.exists(path):
            print("skip %d: no source file" % act)
            continue
        data = parse_file(path)
        with open(os.path.join(OUT, "%d.json" % act), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        kinds = {}
        for s in data["segments"]:
            kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
        print("act %d: %s" % (act, kinds))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main([int(a) for a in sys.argv[1:]])
    else:
        main(list(range(144, 175)))
