"""Mesin Random Forest (C4.5: Entropy, Gain, Split Info, Gain Ratio) - Python murni."""
import math
import random


class Engine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.classes = cfg["classes"]
        self.attrs = cfg["attributes"]
        self.attr_by_key = {a["key"]: a for a in self.attrs}

    # ---------- data ----------
    def to_rows(self, raw):
        rows = []
        for r in raw:
            o = {"no": int(r[0]), "y": r[-1]}
            for i, a in enumerate(self.attrs):
                o[a["key"]] = r[i + 1]
            rows.append(o)
        return rows

    def count(self, rows):
        c = {k: 0 for k in self.classes}
        for r in rows:
            c[r["y"]] += 1
        return c

    def entropy_of_counts(self, c):
        n = sum(c.values())
        e = 0.0
        for k in self.classes:
            if c[k] > 0:
                p = c[k] / n
                e -= p * math.log2(p)
        return abs(e) if abs(e) < 1e-12 else e

    def entropy(self, rows):
        return self.entropy_of_counts(self.count(rows)) if rows else 0.0

    def majority(self, c):
        best = self.classes[-1]
        for k in self.classes:
            if c[k] > c[best]:
                best = k
        return best

    # ---------- evaluasi atribut ----------
    def eval_attr(self, rows, attr):
        n = len(rows)
        e_total = self.entropy(rows)
        gain, si, parts = e_total, 0.0, []
        for v in attr["values"]:
            sub = [r for r in rows if r[attr["key"]] == v]
            if not sub:
                continue
            p = len(sub) / n
            e = self.entropy(sub)
            part = -p * math.log2(p)
            gain -= p * e
            si += part
            parts.append({"value": v, "n": len(sub), "counts": self.count(sub), "entropy": e, "si": abs(part)})
        ratio = gain / si if si > 1e-12 else 0.0
        return {"key": attr["key"], "name": attr["name"], "N": n, "E": e_total,
                "gain": max(gain, 0.0) if abs(gain) < 1e-12 else gain, "si": si, "ratio": ratio, "parts": parts}

    # ---------- bangun pohon ----------
    def _build(self, rows, avail, ctx, path):
        node = {"id": ctx["next"], "path": path, "n": len(rows), "counts": self.count(rows),
                "entropy": self.entropy(rows), "children": [], "leaf": False}
        ctx["next"] += 1
        node["majority"] = self.majority(node["counts"])
        ctx["nodes"][node["id"]] = node
        pure = sum(1 for k in self.classes if node["counts"][k] > 0) == 1
        if pure or not avail:
            node["leaf"] = True
            node["label"] = node["majority"]
            node["reason"] = "pure" if pure else "habis"
            return node
        forced = (ctx["forced"] or {}).get(path)
        cands = forced if forced and all(k in avail for k in forced) else ctx["pick"](avail)
        node["candidates"] = list(cands)
        node["evals"] = [self.eval_attr(rows, self.attr_by_key[k]) for k in cands]
        best = node["evals"][0]
        for ev in node["evals"]:
            if ev["ratio"] > best["ratio"] + 1e-9:
                best = ev
        node["best"] = best["key"]
        for p in best["parts"]:
            sub = [r for r in rows if r[best["key"]] == p["value"]]
            child = self._build(sub, [k for k in avail if k != best["key"]], ctx,
                                f'{path}/{best["key"]}={p["value"]}')
            node["children"].append((p["value"], child))
        return node

    def build_forest(self, rows, mode="modul", n_trees=3, m=2, seed=7):
        rng = random.Random(seed)
        preset = self.cfg.get("preset")
        use_preset = mode == "modul" and preset is not None
        total = len(preset["trees"]) if use_preset else n_trees
        trees = []
        for t in range(total):
            if use_preset:
                nos = list(preset["trees"][t]["bootstrap"])
            else:
                nos = [rng.choice(rows)["no"] for _ in rows]
            by_no = {r["no"]: r for r in rows}
            sample = [by_no[no] for no in nos]
            mm = 2 if use_preset else max(1, min(m, len(self.attrs)))

            def pick(avail, mm=mm):
                return rng.sample(avail, min(mm, len(avail)))

            ctx = {"next": 0, "nodes": {}, "pick": pick,
                   "forced": preset["trees"][t]["candidates"] if use_preset else None}
            root = self._build(sample, [a["key"] for a in self.attrs], ctx, "Root")
            trees.append({"index": t, "bootstrap": nos, "sample": sample,
                          "oob": [r["no"] for r in rows if r["no"] not in nos],
                          "root": root, "nodes": ctx["nodes"]})
        return trees

    # ---------- prediksi ----------
    def predict(self, tree, x):
        node = tree["root"]
        ids = [node["id"]]
        while not node["leaf"]:
            nxt = next((c for v, c in node["children"] if v == x[node["best"]]), None)
            if nxt is None:
                return {"label": node["majority"], "node": node, "ids": ids}
            node = nxt
            ids.append(node["id"])
        return {"label": node["label"], "node": node, "ids": ids}

    def vote(self, trees, x):
        results = [self.predict(t, x) for t in trees]
        tally = {k: 0 for k in self.classes}
        for r in results:
            tally[r["label"]] += 1
        final = self.classes[-1]
        for k in self.classes:
            if tally[k] > tally[final]:
                final = k
        tie = sum(1 for k in self.classes if tally[k] == tally[final]) > 1
        return {"results": results, "tally": tally, "final": final, "tie": tie}
