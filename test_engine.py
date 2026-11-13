"""Uji: hasil mesin Python harus sama dengan laporan (report.json dari versi JS)."""
import json, sys
from data_config import CONFIG
from rf_engine import Engine

E = Engine(CONFIG)
rows = E.to_rows(CONFIG["rows"])
trees = E.build_forest(rows, mode="modul")

def same(py, js):
    if py["leaf"] != js["leaf"] or py["counts"] != js["counts"]:
        return False
    if py["leaf"]:
        return py["label"] == js["label"]
    if py["best"] != js["best"]:
        return False
    for ev, ej in zip(py["evals"], js["evals"]):
        if abs(ev["ratio"] - ej["ratio"]) > 1e-9 or abs(ev["gain"] - ej["gain"]) > 1e-9:
            return False
    return [v for v, _ in py["children"]] == [c["value"] for c in js["children"]] and \
        all(same(c, j["node"]) for (_, c), j in zip(py["children"], js["children"]))

try:
    ref = json.load(open("report.json"))
    for t, r in zip(trees, ref["trees"]):
        assert same(t["root"], r["root"]), "pohon berbeda"
    print("OK: 3 pohon identik dengan laporan")
except FileNotFoundError:
    print("report.json tidak ada, lewati perbandingan")

v = E.vote(trees, CONFIG["test"])
print([r["label"] for r in v["results"]], v["tally"], v["final"])
assert v["final"] == "Ya"
r = E.build_forest(rows, mode="acak", n_trees=5, m=2, seed=42)
print("acak:", len(r), E.vote(r, CONFIG["test"])["final"])
