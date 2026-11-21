"""
app.py - CargoOpt user interface (Streamlit, 100% Python).

IMPORTANT: this file does NO Knapsack calculation.
It collects the truck and the packages, calls the functions in knapsack.py,
and shows the answer as metrics, charts and tables.

Run:  python -m streamlit run app.py
"""

import altair as alt
import pandas as pd
import streamlit as st

from knapsack import STRATEGIES, compare_all, manual_load   # all Knapsack logic lives here

st.set_page_config(page_title="CargoOpt - Truck Load Optimizer", page_icon="🚚", layout="wide")

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
ITEMS_7 = [f"Item {n}" for n in range(1, 8)]
SAMPLES = {
    "Lecture Example 2 (n=7, W=15)": {
        "capacity": 15.0, "names": ITEMS_7,
        "weights": [2, 3, 5, 7, 1, 4, 1], "profits": [10, 5, 15, 7, 6, 18, 3],
        "note": "Matches the lecture slide: 47 (max profit), 54 (min weight), 55.33 (profit / weight).",
    },
    "Lecture Example 1 (n=7, W=15)": {
        "capacity": 15.0, "names": ITEMS_7,
        "weights": [1, 3, 5, 4, 1, 3, 2], "profits": [5, 10, 15, 7, 8, 9, 4],
        "note": "Lecture Example 1: 47.25 (max profit), 46 (min weight), 51 (profit / weight).",
    },
    "Bulk cargo (1000 kg truck)": {
        "capacity": 1000.0, "names": ["Rice", "Sugar", "Cement", "Sand", "Steel rods", "Fertilizer"],
        "weights": [300, 250, 400, 500, 200, 350], "profits": [420, 300, 720, 350, 360, 600], "note": "",
    },
    "Start blank": {"capacity": 100.0, "names": [], "weights": [], "profits": [], "note": ""},
}

# The three Greedy strategies + the user's own load
PLANS = {
    "max_profit": ("Max profit", "Biggest profit first"),
    "min_weight": ("Min weight", "Lightest package first"),
    "max_ratio": ("Profit / weight", "Best profit per unit of weight first"),
    "manual": ("Your load", "The packages you ticked in the Load column"),
}
PALETTE = ["#0f766e", "#2563eb", "#7c3aed", "#db2777", "#ea580c", "#ca8a04",
           "#059669", "#0891b2", "#4f46e5", "#e11d48", "#65a30d", "#9333ea"]
EMPTY_COLOR = "#e5e7eb"


def sample_table(name):
    s = SAMPLES[name]
    # fixed column types, so even an empty table has a checkbox column and number columns
    return pd.DataFrame({
        "Load": pd.Series([False] * len(s["names"]), dtype="bool"),
        "Name": pd.Series(s["names"], dtype="object"),
        "Weight": pd.Series(s["weights"], dtype="float64"),
        "Profit": pd.Series(s["profits"], dtype="float64"),
    })


# ---------------------------------------------------------------------------
# Session state (kept while the browser tab is open)
# ---------------------------------------------------------------------------
if "packages" not in st.session_state:
    first = "Lecture Example 2 (n=7, W=15)"
    st.session_state.packages = sample_table(first)
    st.session_state.capacity = SAMPLES[first]["capacity"]
    st.session_state.dataset = first
    st.session_state.editor_version = 0

if st.session_state.pop("clear_form", False):           # empty the add form after a successful add
    for field in ("f_name", "f_weight", "f_profit"):
        st.session_state.pop(field, None)

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")


def load_dataset():
    """Called when the user picks another dataset."""
    name = st.session_state.dataset
    st.session_state.packages = sample_table(name)
    st.session_state.capacity = SAMPLES[name]["capacity"]
    st.session_state.editor_version += 1          # start a fresh table editor


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def num(value):
    text = f"{value:,.2f}"
    return text[:-3] if text.endswith(".00") else text


# ---------------------------------------------------------------------------
# Sidebar: shipment setup + add package form (same as version 1)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🚚 Shipment")
    st.selectbox("Dataset", list(SAMPLES), key="dataset", on_change=load_dataset)
    st.number_input("Truck capacity", min_value=0.0, step=1.0, key="capacity")
    col_u, col_c = st.columns(2)
    unit = col_u.selectbox("Unit", ["kg", "lb", "ton"])
    currency = col_c.selectbox("Currency", ["$", "Rs", "€", "£"])

    st.divider()
    st.header("➕ Add package")
    with st.form("add_form", border=False):
        st.text_input("Name", key="f_name", max_chars=40, placeholder="e.g. Rice sacks")
        col_w, col_p = st.columns(2)
        col_w.number_input(f"Weight ({unit})", min_value=0.0, step=1.0, value=None, key="f_weight", placeholder="0")
        col_p.number_input(f"Profit ({currency})", min_value=0.0, step=1.0, value=None, key="f_profit", placeholder="0")
        add_clicked = st.form_submit_button("Add package", type="primary", width="stretch")
    form_message = st.empty()


def money(value):
    sep = " " if len(currency) > 1 else ""
    return f"{currency}{sep}{num(value)}"


def weight_text(value):
    return f"{num(value)} {unit}"


capacity = float(st.session_state.capacity)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("CargoOpt")
st.caption("Truck load optimizer · Fractional Knapsack with the three Greedy strategies "
           "from the Week 7 & 8 lecture · all calculations in `knapsack.py`")

# ---------------------------------------------------------------------------
# Packages table: tick "Load" to load a package yourself, click a cell to edit
# ---------------------------------------------------------------------------
st.subheader("Packages")
st.caption("Tick **Load** to build your own load. Click a cell to edit it. "
           "Add a package with the sidebar form or the empty row at the bottom; "
           "select rows and press Delete to remove them.")

edited = st.data_editor(
    st.session_state.packages,
    key=f"editor_{st.session_state.editor_version}",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        "Load": st.column_config.CheckboxColumn("Load", help="Load this package yourself", default=False, width="small"),
        "Name": st.column_config.TextColumn("Package", required=True, max_chars=40, width="medium"),
        "Weight": st.column_config.NumberColumn(f"Weight ({unit})", min_value=0.0, required=True, width="small"),
        "Profit": st.column_config.NumberColumn(f"Profit ({currency})", min_value=0.0, required=True, width="small"),
    },
)

# Add form: handled after the table so the new package keeps the edits made in the table
if add_clicked:
    name = (st.session_state.f_name or "").strip()
    w_in, p_in = st.session_state.f_weight, st.session_state.f_profit
    if not name:
        form_message.error("Enter a package name.")
    elif w_in is None or w_in <= 0:
        form_message.error("Weight must be greater than 0.")
    elif p_in is None or p_in < 0:
        form_message.error("Profit must be 0 or more.")
    else:
        new_row = pd.DataFrame([{"Load": False, "Name": name, "Weight": float(w_in), "Profit": float(p_in)}])
        st.session_state.packages = pd.concat([edited, new_row], ignore_index=True)
        st.session_state.editor_version += 1
        st.session_state.clear_form = True
        st.session_state.flash = f'Added "{name}"'
        st.rerun()

# Keep only complete rows (a new empty row is ignored until it is filled in)
table = edited.copy()
valid = (
    table["Name"].notna() & table["Name"].astype(str).str.strip().ne("")
    & table["Weight"].notna() & (table["Weight"] > 0)
    & table["Profit"].notna() & (table["Profit"] >= 0)
)
packages = table[valid].reset_index(drop=True)
packages["Load"] = packages["Load"].fillna(False).astype(bool)
if (~valid).sum():
    st.caption(f"⚠️ {int((~valid).sum())} row(s) ignored until name, weight (> 0) and profit (≥ 0) are filled in.")

sample = SAMPLES.get(st.session_state.dataset, {})
untouched = (packages[["Name", "Weight", "Profit"]].values.tolist()
             == sample_table(st.session_state.dataset)[["Name", "Weight", "Profit"]].values.tolist())
if sample.get("note") and untouched and capacity == sample["capacity"]:
    st.info(sample["note"], icon="📘")

if packages.empty:
    st.info("No packages yet. Add one with the sidebar form or the empty row in the table.", icon="📦")
    st.stop()
if capacity <= 0:
    st.warning("Truck capacity must be greater than 0.", icon="⚠️")
    st.stop()

# ---------------------------------------------------------------------------
# Ask knapsack.py for the answers
# ---------------------------------------------------------------------------
names = packages["Name"].astype(str).tolist()
weights = packages["Weight"].astype(float).tolist()
profits = packages["Profit"].astype(float).tolist()
chosen = [i for i, ticked in enumerate(packages["Load"]) if ticked]

answer = compare_all(profits, weights, capacity)          # the three Greedy strategies
manual_error = None
try:
    manual = manual_load(profits, weights, capacity, chosen)   # "Your load"
except ValueError as error:
    manual, manual_error = None, str(error)

results = dict(answer["strategies"])
if manual and manual["steps"]:
    results["manual"] = manual
best_profit = max(answer["strategies"][k]["total_profit"] for k in STRATEGIES)


def color_of(index):
    return PALETTE[index % len(PALETTE)]


def truck_chart(steps):
    """Horizontal bar = the truck. Each coloured block is a package, grey = empty space."""
    rows, start = [], 0.0
    for s in steps:
        i = s["item"]
        end = start + s["weight_taken"]
        partial = s["fraction"] < 0.999999
        rows.append({"truck": "Truck", "label": f"{i + 1}. {names[i]}" + (" (partial)" if partial else ""), "num": str(i + 1),
                     "start": start, "end": end, "mid": (start + end) / 2, "color": color_of(i),
                     "taken": f"{round(s['fraction'] * 100)}%", "weight": weight_text(s["weight_taken"]),
                     "profit": money(s["profit_gained"])})
        start = end
    if start < capacity - 1e-9:
        rows.append({"truck": "Truck", "label": "Empty space", "num": "", "start": start, "end": capacity, "mid": (start + capacity) / 2,
                     "color": EMPTY_COLOR, "taken": "-", "weight": weight_text(capacity - start), "profit": "-"})
    data = pd.DataFrame(rows)

    # wide blocks show the package name, narrow blocks only its number
    data["text"] = [r["label"].split(" (")[0] if (r["end"] - r["start"]) > capacity * 0.18 else r["num"] for r in rows]
    x = alt.X("start:Q", scale=alt.Scale(domain=[0, capacity], nice=False), title=f"Truck capacity ({unit})",
              axis=alt.Axis(grid=False, tickCount=6))
    y = alt.Y("truck:N", axis=None)
    bars = alt.Chart(data).mark_bar(size=56, cornerRadius=6, stroke="white", strokeWidth=2).encode(
        x=x, x2="end:Q", y=y,
        color=alt.Color("label:N", scale=alt.Scale(domain=data["label"].tolist(), range=data["color"].tolist()),
                        legend=None),
        tooltip=[alt.Tooltip("label:N", title="Package"), alt.Tooltip("taken:N", title="Loaded"),
                 alt.Tooltip("weight:N", title="Weight"), alt.Tooltip("profit:N", title="Profit")],
    )
    width_ok = (data["end"] - data["start"]) > capacity * 0.04
    labels = alt.Chart(data[width_ok]).mark_text(color="white", fontWeight="bold", fontSize=13).encode(
        x="mid:Q", y=y, text="text:N")
    return (bars + labels).properties(height=110).configure_view(stroke=None)


def rule_column(key):
    return {"max_profit": "Profit", "min_weight": "Weight", "max_ratio": "Profit / weight"}.get(key)


def show_plan(key):
    short, rule = PLANS[key]
    if key == "manual":
        if manual_error:
            st.error(manual_error, icon="⚠️")
            return
        if not chosen:
            st.info("Tick packages in the **Load** column of the table to build your own load, "
                    "then compare it with the Greedy strategies.", icon="☑️")
            return
    plan = results[key]
    st.caption(f"**{short}:** {rule}.")

    gap = best_profit - plan["total_profit"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Profit", money(plan["total_profit"]),
              delta="Best" if gap < 1e-9 else f"-{money(gap)} vs best",
              delta_color="normal")
    c2.metric("Loaded", f"{num(plan['total_weight'])} / {weight_text(capacity)}")
    c3.metric("Utilization", f"{round(plan['total_weight'] / capacity * 100)}%")

    st.markdown("**Truck load**")
    st.altair_chart(truck_chart(plan["steps"]), width="stretch")

    st.markdown("**Loading sequence**")
    seq = pd.DataFrame([{
        "Step": n,
        "Package": f"{s['item'] + 1}. {names[s['item']]}",
        "Sorted by": (num(s["key"]) if key != "manual" else "your pick"),
        "Loaded": round(s["fraction"] * 100, 1),
        f"Weight ({unit})": s["weight_taken"],
        f"Profit added ({currency})": s["profit_gained"],
        f"Space left ({unit})": s["remaining"],
    } for n, s in enumerate(plan["steps"], start=1)])
    sort_label = rule_column(key) or "Sorted by"
    st.dataframe(
        seq.rename(columns={"Sorted by": sort_label}), hide_index=True, width="stretch",
        column_config={
            "Loaded": st.column_config.ProgressColumn("Loaded", min_value=0, max_value=100, format="%.0f%%"),
            f"Weight ({unit})": st.column_config.NumberColumn(format="%.2f"),
            f"Profit added ({currency})": st.column_config.NumberColumn(format="%.2f"),
            f"Space left ({unit})": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    left_out = [f"{i + 1}. {names[i]}" for i in range(len(names)) if i not in {s["item"] for s in plan["steps"]}]
    if left_out:
        st.caption("Not loaded: " + ", ".join(left_out))

    csv = seq.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export this plan (CSV)", csv, file_name=f"cargo-plan-{key}.csv",
                       mime="text/csv", key=f"csv_{key}")


# ---------------------------------------------------------------------------
# Load plan: one tab per strategy
# ---------------------------------------------------------------------------
st.subheader("Load plan")
tab_labels = []
for key, (short, _) in PLANS.items():
    if key in results:
        star = " ★" if key in answer["best"] else ""
        tab_labels.append(f"{short} · {money(results[key]['total_profit'])}{star}")
    else:
        tab_labels.append(f"{short} · -")
for tab, key in zip(st.tabs(tab_labels), PLANS):
    with tab:
        show_plan(key)

# ---------------------------------------------------------------------------
# Strategy comparison
# ---------------------------------------------------------------------------
st.subheader("Strategy comparison")
compare_rows = []
for key, (short, rule) in PLANS.items():
    if key not in results:
        continue
    profit = results[key]["total_profit"]
    compare_rows.append({
        "Strategy": short, "Rule": rule, "Profit": profit,
        "vs best": profit - best_profit,
        "Loaded": results[key]["total_weight"],
        "Best": key in answer["best"],
    })
compare = pd.DataFrame(compare_rows)

chart_left, table_right = st.columns([1, 1], gap="large")
with chart_left:
    base = alt.Chart(compare).encode(
        y=alt.Y("Strategy:N", sort=None, title=None),
        x=alt.X("Profit:Q", title=f"Total profit ({currency})"),
    )
    bars = base.mark_bar(cornerRadiusEnd=6, size=26).encode(
        color=alt.when(alt.datum.Best).then(alt.value("#0f766e")).otherwise(alt.value("#94a3b8")),
        tooltip=["Strategy", "Rule", alt.Tooltip("Profit:Q", format=",.2f")],
    )
    text = base.mark_text(align="left", dx=6, fontWeight="bold").encode(text=alt.Text("Profit:Q", format=",.2f"))
    st.altair_chart((bars + text).properties(height=48 * len(compare) + 30).configure_view(stroke=None),
                    width="stretch")
with table_right:
    st.dataframe(
        compare.drop(columns=["Best", "Rule"]), hide_index=True, width="stretch",
        column_config={
            "Profit": st.column_config.NumberColumn(f"Profit ({currency})", format="%.2f"),
            "vs best": st.column_config.NumberColumn(f"vs best ({currency})", format="%.2f"),
            "Loaded": st.column_config.NumberColumn(f"Loaded ({unit})", format="%.2f"),
        },
    )

winners = " and ".join(STRATEGIES[k] for k in answer["best"])
if "manual" in results:
    share = round(results["manual"]["total_profit"] / best_profit * 100) if best_profit else 0
    st.info(f"Your load earns **{share}%** of the best Greedy plan "
            f"({money(results['manual']['total_profit'])} of {money(best_profit)}).", icon="☑️")
if len(answer["best"]) == len(STRATEGIES):
    st.success("All three Greedy strategies earn the same on this shipment.", icon="✅")
else:
    st.success(f"**{winners}** earns the most. For Fractional Knapsack, choosing by profit / weight is always optimal.",
               icon="🏆")

# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------
with st.expander("How it works"):
    st.markdown(
        """
**Fractional Knapsack:** the truck holds a limited weight, and part of a package may be loaded.
Greedy picks the package that looks best at each step and never goes back.

| Strategy | Rule |
|---|---|
| Maximum profit | biggest profit first |
| Minimum weight | lightest package first |
| Maximum profit / weight | best profit per unit of weight first (optimal) |

**Where is the code?** Everything is calculated in `knapsack.py`:
`choose_order()` sorts the packages, `fractional_knapsack()` fills the truck,
`compare_all()` runs the three strategies, and `manual_load()` totals your ticked packages.
`app.py` only shows the results.
"""
    )
