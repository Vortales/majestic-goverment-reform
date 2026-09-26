# -*- coding: utf-8 -*-
"""index.py — собирает ACT/00_Индекс_ACT.md по данным tools/data/actNNN.py и файлам ACT/*.docx."""
import sys, importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "data"))

NUMS = [n for n in range(144, 175) if n != 151]

# Как обозначить строки, не привязанные к отдельной статье (структурные правки)
MANUAL_LABEL = {
    144: "структура кодекса (разделы и главы)",
    145: "структура кодекса (разделы и главы)",
    146: "структура кодекса (главы, новая глава 15)",
    149: "ст. 37 и новый Раздел II «Обязательственное право» (ст. 38 – 53)",
    154: "структура приложения и оглавление",
    172: "наименование закона",
}
out = []
out.append("# Индекс актов о внесении изменений (ACT. 144 – ACT. 174)\n")
out.append("Каждый файл в папке `ACT/` оформлен по форме Приложения № 2 — о внесении изменений в "
           "действующий закон: заголовок «ACT. NNN», «IN THE SENATE OF THE STATE OF SAN ANDREAS», "
           "«MARCH 00, 2026», «ЗАКОНОПРОЕКТ о внесении изменений в действующий закон», "
           "«SECTION 1. СУТЬ ПРАВКИ», «SECTION 2. ВНЕСЕНИЕ ПРАВКИ В …» и таблица из двух колонок "
           "(«настоящая редакция» / «предложенный вариант»). В левой колонке изменяемый фрагмент выделен "
           "красным, в правой — зелёным. АКТ. 151 отсутствует: акт с этим номером не содержит изменений.\n")
out.append("| АКТ | Закон (SECTION 2) | Статьи и положения | Строк |")
out.append("|---|---|---|---|")

total_rows = 0
details = []
for n in NUMS:
    mod = importlib.import_module(f"act{n}")
    doc = mod.DOC
    arts = []
    for row in doc["rows"]:
        if row["src"]:
            a = str(row["src"][1])
            if a not in arts:
                arts.append(a)
        else:
            label = MANUAL_LABEL.get(n, "структура акта")
            if label not in arts:
                arts.append(label)
    total_rows += len(doc["rows"])
    name = doc["section2"]
    pre = "п. " if n == 163 else "ст. "
    cells = ", ".join(a if a in MANUAL_LABEL.values() or a == "структура акта" else pre + a for a in arts)
    out.append(f"| **ACT.{n}** | {name} | {cells} | {len(doc['rows'])} |")
    details.append((n, name, arts, doc))

out.append("")
out.append(f"Всего актов: **{len(NUMS)}**, всего строк сравнения: **{total_rows}**.\n")
out.append("---\n")
out.append("## Состав правок по актам\n")
for n, name, arts, doc in details:
    out.append(f"### ACT.{n} — {name}\n")
    for line in doc["essence"]:
        out.append(f"- {line}")
    out.append("")
    pre2 = "пункт " if n == 163 else "статья "
    out.append("*Затронутые положения:* "
               + ", ".join(a if a in MANUAL_LABEL.values() or a == "структура акта" else pre2 + a for a in arts) + ".\n")
    if doc.get("notes"):
        out.append("*Примечания к акту:*")
        for note in doc["notes"]:
            out.append(f"- {note}")
        out.append("")

Path(ROOT / "ACT" / "00_Индекс_ACT.md").write_text("\n".join(out), encoding="utf-8")
print("OK", ROOT / "ACT" / "00_Индекс_ACT.md", "строк сравнения:", total_rows)
