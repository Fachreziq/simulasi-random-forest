"""Simulasi Random Forest (Streamlit). Jalankan: streamlit run app.py"""
import pandas as pd
import streamlit as st

from data_config import CONFIG
from rf_engine import Engine

E = Engine(CONFIG)
CLS = CONFIG["classes"]
ATTRS = CONFIG["attributes"]
LABEL = CONFIG["label"]
NAME = {a["key"]: a["name"] for a in ATTRS}

st.set_page_config(page_title="Simulasi Random Forest", page_icon="🌲", layout="wide")


def f6(x):
    if abs(x) < 5e-7:
        x = 0.0
    return f"{x:.6f}".replace(".", ",")


def path_label(p):
    if p == "Root":
        return "Node akar"
    out = []
    for s in p.split("/")[1:]:
        k, v = s.split("=")
        out.append(f"{NAME[k]} = {v}")
    return " → ".join(out)


def ent_terms(c, n):
    t = [f"(-{c[k]}/{n} * log2({c[k]}/{n}))" for k in CLS if c[k] > 0]
    return " + ".join(t) if t else "0"


def number_nodes(node, num="1", acc=None):
    """Beri nomor hierarkis (1, 1.1, 1.2, ...) pada setiap node internal."""
    acc = {} if acc is None else acc
    if not node["leaf"]:
        acc[node["id"]] = num
        for i, (_, ch) in enumerate(node["children"], start=1):
            number_nodes(ch, f"{num}.{i}", acc)
    return acc


def dot_tree(tree, hot_ids=None, selected=None):
    hot = set(hot_ids or [])
    lines = [
        "digraph G {", "rankdir=TB;",
        'node [fontname="Helvetica", fontsize=11, style=filled, fillcolor="#92D050", fontcolor="white", color="#92D050"];',
        'edge [fontname="Helvetica", fontsize=10, color="#92D050"];',
    ]

    def rec(n):
        title = n["label"] if n["leaf"] else NAME[n["best"]]
        sub = " · ".join(f"{n['counts'][c]} {c}" for c in CLS)
        shape = 'shape=box, style="rounded,filled"' if n["leaf"] else "shape=ellipse"
        extra = ', color="#0e5a78", penwidth=3' if selected == n["id"] else ""
        extra += ', color="#F4793B", penwidth=3' if n["id"] in hot and selected != n["id"] else ""
        lines.append(f'n{n["id"]} [label="{title}\\n{sub}", {shape}{extra}];')
        for v, ch in n["children"]:
            on = n["id"] in hot and ch["id"] in hot
            style = ', color="#F4793B", penwidth=3' if on else ""
            lines.append(f'n{n["id"]} -> n{ch["id"]} [label="{v}"{style}];')
            rec(ch)

    rec(tree["root"])
    lines.append("}")
    return "\n".join(lines)


def data_df(rows, with_order=False):
    cols = (["Urutan"] if with_order else []) + ["No"] + [a["name"] for a in ATTRS] + [LABEL]
    data = []
    for i, r in enumerate(rows, start=1):
        data.append(([i] if with_order else []) + [r["no"]] + [r[a["key"]] for a in ATTRS] + [r["y"]])
    return pd.DataFrame(data, columns=cols)


def show_node_detail(node, num):
    st.markdown(f"#### Node {num}: {path_label(node['path'])}")
    st.write(f"{node['n']} data: " + ", ".join(f"{node['counts'][c]} {c}" for c in CLS) + ".")
    st.code(f"Entropy(S) = {ent_terms(node['counts'], node['n'])} = {f6(node['entropy'])}", language=None)
    st.write("Atribut acak yang dipertimbangkan (m = %d): **%s**" %
             (len(node["candidates"]), ", ".join(NAME[k] for k in node["candidates"])))
    for ev in node["evals"]:
        win = ev["key"] == node["best"]
        st.markdown(f"**{ev['name']}**" + ("  ✅ dipilih" if win else ""))
        tbl = pd.DataFrame([
            [p["value"], p["n"], *[p["counts"][c] for c in CLS], f6(p["entropy"]), f6(p["si"])]
            for p in ev["parts"]
        ], columns=["Nilai", "Jumlah", *CLS, "Entropy", "Split Info"])
        st.dataframe(tbl, hide_index=True)
        gain_terms = " + ".join(f"({p['n']}/{ev['N']} * {f6(p['entropy'])})" for p in ev["parts"])
        si_terms = " + ".join(f"(-{p['n']}/{ev['N']} * log2({p['n']}/{ev['N']}))" for p in ev["parts"])
        st.code(
            f"Gain       = {f6(ev['E'])} - ({gain_terms}) = {f6(ev['gain'])}\n"
            f"Split Info = {si_terms} = {f6(ev['si'])}\n"
            f"Gain Ratio = {f6(ev['gain'])} / {f6(ev['si'])} = {f6(ev['ratio'])}",
            language=None)
    st.success(f"Gain Ratio tertinggi: {NAME[node['best']]}, jadi node dibagi berdasarkan {NAME[node['best']]}.")


# =====================================================================
st.title("🌲 Simulasi Random Forest")
st.caption(CONFIG["title"])

tab_data, tab_forest, tab_tree, tab_pred = st.tabs(["1. Data", "2. Hutan", "3. Pohon", "4. Prediksi"])

# ---------------- 1. data ----------------
base_df = data_df(E.to_rows(CONFIG["rows"]))
with tab_data:
    st.subheader("Data pelanggan")
    st.write(f"Setiap baris adalah satu pelanggan. Atribut dipakai untuk memprediksi kolom **{LABEL}**. "
             "Nilai pada tabel bisa diubah.")
    colcfg = {a["name"]: st.column_config.SelectboxColumn(options=a["values"], required=True) for a in ATTRS}
    colcfg[LABEL] = st.column_config.SelectboxColumn(options=CLS, required=True)
    edited_df = st.data_editor(base_df, hide_index=True, disabled=["No"], column_config=colcfg, key="editor")
    edited = not edited_df.reset_index(drop=True).equals(base_df)
    raw_rows = edited_df.values.tolist()
    rows = E.to_rows(raw_rows)
    counts = E.count(rows)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah data", len(rows))
    for col, k in zip((c2, c3), CLS):
        col.metric(k, counts[k])
    c4.metric("Entropy total", f6(E.entropy_of_counts(counts)))
    if edited:
        st.info("Data sudah diubah, jadi mode “Sesuai laporan” dinonaktifkan "
                "(hasil bootstrap pada laporan dibuat dari data awal).")

# ---------------- 2. hutan ----------------
with tab_forest:
    st.subheader("Atur hutan dan bootstrap sampling")
    st.write(f"Setiap pohon dilatih dari sampel bootstrap: {len(rows)} data diambil acak dengan pengembalian, "
             "sehingga satu data bisa muncul lebih dari sekali dan sebagian tidak terpilih. "
             "Pada tiap node dipilih **m** atribut acak, lalu atribut dengan Gain Ratio tertinggi dipakai untuk membagi data.")
    options = ["Acak dengan seed"] if edited else ["Sesuai laporan (3 pohon, m = 2)", "Acak dengan seed"]
    mode_label = st.radio("Mode", options, horizontal=True)
    mode = "modul" if mode_label.startswith("Sesuai") else "acak"
    cA, cB, cC = st.columns(3)
    n_trees = cA.number_input("Jumlah pohon", 1, 9, 3, disabled=(mode == "modul"))
    m_attr = cB.number_input("m (atribut per node)", 1, len(ATTRS), 2, disabled=(mode == "modul"))
    seed = cC.number_input("Seed", value=7, step=1, disabled=(mode == "modul"))
    trees = E.build_forest(rows, mode=mode, n_trees=int(n_trees), m=int(m_attr), seed=int(seed))

    st.markdown("##### Tabel sampel bootstrap")
    boot_tabs = st.tabs([f"Pohon {t['index'] + 1}" for t in trees])
    for bt, t in zip(boot_tabs, trees):
        with bt:
            st.dataframe(data_df(t["sample"], with_order=True), hide_index=True)
            st.write("No terpilih: **" + ", ".join(map(str, t["bootstrap"])) + "**")
            st.write("Tidak terpilih (out-of-bag): **" + (", ".join(map(str, t["oob"])) or "-") + "**")

# ---------------- 3. pohon ----------------
with tab_tree:
    st.subheader("Pohon keputusan")
    st.write("Pilih node pada daftar untuk melihat perhitungan Entropy, Gain, Split Info, dan Gain Ratio. "
             "Node yang dipilih diberi garis biru.")
    tree_tabs = st.tabs([f"Pohon {t['index'] + 1}" for t in trees])
    for tt, t in zip(tree_tabs, trees):
        with tt:
            nums = number_nodes(t["root"])
            labels = {nid: f"Node {num}: {path_label(t['nodes'][nid]['path'])}" for nid, num in nums.items()}
            ids = list(nums.keys())
            sel = st.selectbox("Node", ids, format_func=lambda i, lb=labels: lb[i], key=f"node_{t['index']}")
            st.graphviz_chart(dot_tree(t, selected=sel))
            show_node_detail(t["nodes"][sel], nums[sel])

# ---------------- 4. prediksi ----------------
with tab_pred:
    st.subheader("Klasifikasi data baru dengan voting mayoritas")
    st.write("Data baru dijalankan di setiap pohon. Kelas yang paling banyak dipilih menjadi hasil akhir.")
    cols = st.columns(len(ATTRS))
    x = {}
    for col, a in zip(cols, ATTRS):
        default = CONFIG["test"][a["key"]]
        x[a["key"]] = col.selectbox(a["name"], a["values"], index=a["values"].index(default), key=f"test_{a['key']}")
    v = E.vote(trees, x)
    vcols = st.columns(len(trees))
    for vc, t, r in zip(vcols, trees, v["results"]):
        with vc:
            st.markdown(f"**Pohon {t['index'] + 1}**")
            st.metric("Hasil", r["label"])
            st.caption(path_label(r["node"]["path"]) if r["node"]["path"] != "Root" else "Langsung di akar")
    st.write("Hasil voting: **" + " : ".join(f"{v['tally'][k]} {k}" for k in CLS) + "**")
    (st.success if v["final"] == CLS[-1] else st.warning)(f"{LABEL}: **{v['final']}**"
        + (" (suara seimbang, dipilih kelas terakhir)" if v["tie"] else ""))
    st.markdown("##### Jalur pada pohon")
    path_tabs = st.tabs([f"Pohon {t['index'] + 1}" for t in trees])
    for pt, t, r in zip(path_tabs, trees, v["results"]):
        with pt:
            st.graphviz_chart(dot_tree(t, hot_ids=r["ids"]))
