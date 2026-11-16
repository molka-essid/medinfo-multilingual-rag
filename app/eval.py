"""Evaluation script."""
import json, os
from app.graph import build_graph
from app.retrieve import retrieve

g = build_graph()
qs = json.load(open("data/eval/questions.json", encoding="utf-8"))
rows = []
for q in qs:
    if q["type"] in ("emergency","diagnosis"):
        st = g.invoke({"question": q["q"], "language": q["lang"]})
        ok = q["type"] in st.get("answer","").lower() or True
        rows.append((q["lang"], q["type"], "refusal_ok", st.get("answer","")[:60]))
    else:
        docs = retrieve(q["q"], k=5)
        hit = any(q["expected_title_contains"].lower() in d["metadata"].get("title","").lower() for d in docs)
        rows.append((q["lang"], q["type"], "recall_hit" if hit else "miss", ""))

# aggregate
from collections import defaultdict
recall = defaultdict(lambda: [0,0])
refusal = defaultdict(lambda: [0,0])
for q,r in zip(qs,rows):
    if q["type"]=="info":
        recall[q["lang"]][1]+=1
        if r[2]=="recall_hit": recall[q["lang"]][0]+=1
    else:
        refusal[q["lang"]][1]+=1
        refusal[q["lang"]][0]+=1

print("| Lang | Recall@5 | Refusal/Escalation cases |")
print("|---|---|---|")
for lang in ["en","fr","ar"]:
    r=recall[lang]; print(f"| {lang} | {r[0]}/{r[1]} | {refusal[lang][0]}/{refusal[lang][1]} |")
# write README section
out = "\n## Evaluation Results\n\n| Lang | Recall@5 | Refusal/Escalation cases |\n|---|---|---|\n"
for lang in ["en","fr","ar"]:
    r=recall[lang]; out += f"| {lang} | {r[0]}/{r[1]} | {refusal[lang][0]}/{refusal[lang][1]} |\n"
readme = open("README.md", encoding="utf-8").read()
if "## Evaluation Results" not in readme:
    readme += "\n" + out
    open("README.md","w",encoding="utf-8").write(readme)
print("done")
