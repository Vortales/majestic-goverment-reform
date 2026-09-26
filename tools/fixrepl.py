import re,sys
from pathlib import Path
for f in sys.argv[1:]:
    p=Path(f); lines=p.read_text(encoding="utf-8").split("\n")
    out=[]; inside=False
    for ln in lines:
        st=ln.strip()
        if st.startswith("repl=["):
            inside=True; out.append(ln); continue
        if inside:
            if st=="],":
                inside=False; out.append(ln); continue
            if re.match(r'^(note_old|note_new|add)=', st) or st=="),":
                out.append("            ],"); inside=False; out.append(ln); continue
        out.append(ln)
    p.write_text("\n".join(out), encoding="utf-8")
    print("fixed", f)
