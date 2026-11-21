"""
app.py - CargoOpt page (Streamlit, Python).

IMPORTANT: this file does NO Knapsack calculation.
  knapsack.py -> all the Knapsack logic (Greedy strategies, your own load)
  ui.py       -> our design (cards, truck drawing, timeline, comparison)
  app.py      -> puts the page together: reads input, calls knapsack.py, shows the result with ui.py

Run:  python -m streamlit run app.py
"""

import pandas as pd
import streamlit as st

import ui
from knapsack import STRATEGIES, compare_all, manual_load   # all Knapsack logic lives here

st.set_page_config(page_title="CargoOpt - Truck Load Optimizer", page_icon="🚚", layout="wide",
                   initial_sidebar_state="collapsed")
st.html(ui.CSS)
st.html(ui.app_bar())

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
    "max_profit": ("Max profit", "Maximum profit", "Biggest profit first"),
    "min_weight": ("Min weight", "Minimum weight", "Lightest package first"),
    "max_ratio": ("Profit / wt", "Maximum profit / weight", "Best profit per unit of weight first"),
    "manual": ("Your load", "Your load", "The packages you ticked in the Load column"),
}


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
    st.session_state.strategy = "max_ratio"

if st.session_state.pop("clear_form", False):           # empty the add form after a successful add
    for field in ("f_name", "f_weight", "f_profit"):
        st.session_state.pop(field, None)

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

if st.session_state.get("strategy") is None:            # clicking the selected strategy again un-selects it
    st.session_state.strategy = st.session_state.get("last_strategy", "max_ratio")
st.session_state.last_strategy = st.session_state.strategy


def load_dataset():
    """Called when the user picks another dataset."""
    name = st.session_state.dataset
    st.session_state.packages = sample_table(name)
    st.session_state.capacity = SAMPLES[name]["capacity"]
    st.session_state.editor_version += 1          # start a fresh table editor


# ---------------------------------------------------------------------------
# Layout: left = setup + add form, right = results (cards are filled further down)
# ---------------------------------------------------------------------------
left, right = st.columns([1, 1.9], gap="medium")

with left:
    with st.container(key="card_setup"):
        st.html(ui.card_head("Shipment", "Pick a dataset or build your own."))
        st.selectbox("Dataset", list(SAMPLES), key="dataset", on_change=load_dataset)
        note_slot = st.empty()
        c_cap, c_unit, c_cur = st.columns([1.3, 1, 1])
        c_cap.number_input("Capacity", min_value=0.0, step=1.0, key="capacity")
        unit = c_unit.selectbox("Unit", ["kg", "lb", "ton"])
        currency = c_cur.selectbox("Currency", ["$", "Rs", "€", "£"])

    with st.container(key="card_add"):
        st.html(ui.card_head("Add package", "Name, weight and profit of one package."))
        with st.form("add_form", border=False):
            st.text_input("Name", key="f_name", max_chars=40, placeholder="e.g. Rice sacks")
            c_w, c_p = st.columns(2)
            c_w.number_input(f"Weight ({unit})", min_value=0.0, step=1.0, value=None, key="f_weight", placeholder="0")
            c_p.number_input(f"Profit ({currency})", min_value=0.0, step=1.0, value=None, key="f_profit", placeholder="0")
            add_clicked = st.form_submit_button("＋ Add package", type="primary", width="stretch")
        form_message = st.empty()

with right:
    plan_card = st.container(key="card_plan")
    packages_card = st.container(key="card_packages")
    compare_card = st.container(key="card_compare")
    about_card = st.container(key="card_about")

capacity = float(st.session_state.capacity)


def num(value):
    text = f"{value:,.2f}"
    return text[:-3] if text.endswith(".00") else text


def money(value):
    return f"{currency}{' ' if len(currency) > 1 else ''}{num(value)}"


def wt(value):
    return f"{num(value)} {unit}"


# ---------------------------------------------------------------------------
# Packages card: tick "Load" to load a package yourself, click a cell to edit
# ---------------------------------------------------------------------------
with packages_card:
    head_slot = st.empty()
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
    footer_slot = st.empty()

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
valid = (
    edited["Name"].notna() & edited["Name"].astype(str).str.strip().ne("")
    & edited["Weight"].notna() & (edited["Weight"] > 0)
    & edited["Profit"].notna() & (edited["Profit"] >= 0)
)
packages = edited[valid].reset_index(drop=True)
packages["Load"] = packages["Load"].fillna(False).astype(bool)
ignored = int((~valid).sum())

head_slot.html(ui.card_head(
    "Packages",
    "Tick Load to load a package yourself. Click a cell to edit; add a row at the bottom; select rows and press Delete to remove.",
    count=len(packages)))

sample = SAMPLES.get(st.session_state.dataset, {})
untouched = (packages[["Name", "Weight", "Profit"]].values.tolist()
             == sample_table(st.session_state.dataset)[["Name", "Weight", "Profit"]].values.tolist())
if sample.get("note") and untouched and capacity == sample["capacity"]:
    note_slot.html(ui.callout(sample["note"]))

# ---------------------------------------------------------------------------
# Nothing to calculate yet?
# ---------------------------------------------------------------------------
problem = None
if packages.empty:
    problem = ("No packages yet", "Add one with the form or the empty row in the table.")
elif capacity <= 0:
    problem = ("Truck capacity is 0", "Set a capacity greater than 0 in Shipment.")
if problem:
    with plan_card:
        st.html(ui.card_head("Load plan", "Step-by-step Greedy loading"))
        st.html(ui.empty(*problem))
    with compare_card:
        st.html(ui.card_head("Strategy comparison", "Total profit of each rule on the same shipment."))
        st.html('<p class="rule">The comparison appears once there are packages to load.</p>')
    st.html(ui.footer())
    st.stop()

# ---------------------------------------------------------------------------
# Ask knapsack.py for the answers
# ---------------------------------------------------------------------------
names = packages["Name"].astype(str).tolist()
weights = packages["Weight"].astype(float).tolist()
profits = packages["Profit"].astype(float).tolist()
chosen = [i for i, ticked in enumerate(packages["Load"]) if ticked]

answer = compare_all(profits, weights, capacity)              # the three Greedy strategies
manual_error = None
try:
    manual = manual_load(profits, weights, capacity, chosen)   # "Your load"
except ValueError as error:
    manual, manual_error = None, str(error)

results = dict(answer["strategies"])
if manual and manual["steps"]:
    results["manual"] = manual
best_profit = max(answer["strategies"][k]["total_profit"] for k in STRATEGIES)

# footer under the table: your own load
ticked_weight = sum(weights[i] for i in chosen)
footer_slot.html(ui.load_footer(
    len(chosen), wt(ticked_weight), wt(capacity),
    money(manual["total_profit"]) if manual else "-", wt(max(0.0, capacity - ticked_weight)),
    over=manual_error is not None))
if ignored:
    with packages_card:
        st.caption(f"{ignored} row(s) ignored until name, weight (> 0) and profit (≥ 0) are filled in.")

# ---------------------------------------------------------------------------
# Load plan card
# ---------------------------------------------------------------------------
def option_label(key):
    short = PLANS[key][0]                       # two lines: name, then profit in bold
    if key not in results:
        return f"{short}  \n**–**"
    star = " ★" if key in answer["best"] else ""
    return f"{short}{star}  \n**{money(results[key]['total_profit'])}**"


def sort_text(key, step):
    if key == "max_profit":
        return f"profit {money(step['key'])}"
    if key == "min_weight":
        return f"weight {wt(step['key'])}"
    if key == "max_ratio":
        return f"profit/weight {step['key']:.2f}"
    return "your pick"


with plan_card:
    head_col, export_col = st.columns([3, 1], vertical_alignment="center")
    head_col.html(ui.card_head("Load plan", "Step-by-step Greedy loading"))
    st.segmented_control("Strategy", list(PLANS), key="strategy", format_func=option_label,
                         label_visibility="collapsed", width="stretch")
    key = st.session_state.strategy or "max_ratio"
    short, full_name, rule = PLANS[key]
    st.html(f'<p class="rule">{full_name}: {rule.lower()}.</p>')

    if key == "manual" and manual_error:
        st.html(ui.callout(manual_error, bad=True))
    elif key == "manual" and not chosen:
        st.html(ui.empty("Nothing ticked yet",
                         "Tick packages in the Load column of the table, then compare your load with Greedy."))
    else:
        plan = results[key]
        gap = best_profit - plan["total_profit"]
        st.html(ui.stats(
            money(plan["total_profit"]),
            "Best" if gap < 1e-9 else f"−{money(gap)} vs best", gap < 1e-9,
            num(plan["total_weight"]), wt(capacity),
            f"{round(plan['total_weight'] / capacity * 100)}%"))
        st.html(ui.truck(plan["steps"], capacity, wt(capacity)))

        rows = []
        for s in plan["steps"]:
            i = s["item"]
            partial = s["fraction"] < ui.FULL
            took = (f"took {round(s['fraction'] * 100)}% ({wt(s['weight_taken'])} of {wt(weights[i])})" if partial
                    else f"took all {wt(s['weight_taken'])}")
            rows.append({"item": i, "name": names[i], "partial": partial,
                         "detail": f"{sort_text(key, s)} · {took} · {wt(s['remaining'])} left",
                         "gain": money(s["profit_gained"])})
        st.html(ui.timeline(rows, len(plan["steps"]), len(names)))

        csv = pd.DataFrame([{
            "Step": n, "Package": names[s["item"]], "Percent loaded": round(s["fraction"] * 100, 1),
            f"Weight loaded ({unit})": s["weight_taken"], f"Profit added ({currency})": s["profit_gained"],
            f"Space left ({unit})": s["remaining"],
        } for n, s in enumerate(plan["steps"], start=1)]).to_csv(index=False).encode("utf-8")
        export_col.download_button("⬇ Export", csv, file_name=f"cargo-plan-{key}.csv", mime="text/csv", width="stretch")

# ---------------------------------------------------------------------------
# Strategy comparison card
# ---------------------------------------------------------------------------
with compare_card:
    st.html(ui.card_head("Strategy comparison", "Total profit of each Greedy rule on the same shipment."))
    rows = []
    for k, (short, full_name, rule) in PLANS.items():
        if k not in results:
            continue
        profit = results[k]["total_profit"]
        gap = best_profit - profit
        rows.append({"name": full_name, "desc": rule, "value": money(profit),
                     "pct": min(100.0, profit / best_profit * 100) if best_profit > 0 else 0.0,
                     "best": k in answer["best"], "gap": money(gap) if gap > 1e-9 else None})
    st.html(ui.comparison(rows))

    if "manual" in results:
        share = round(results["manual"]["total_profit"] / best_profit * 100) if best_profit else 0
        note = (f"Your load earns <b>{share}%</b> of the best Greedy plan "
                f"({money(results['manual']['total_profit'])} of {money(best_profit)}).")
    elif len(answer["best"]) == len(STRATEGIES):
        note = "All three Greedy strategies earn the same on this shipment."
    else:
        note = ("<b>Maximum profit / weight</b> earns the most. For Fractional Knapsack, choosing by profit / weight "
                "is always optimal. Tick packages in the table to try to beat it yourself.")
    st.html(ui.callout(note))

# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------
with about_card:
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

**Where is the code?** All calculations are in `knapsack.py`: `choose_order()` sorts the packages,
`fractional_knapsack()` fills the truck, `compare_all()` runs the three strategies and `manual_load()`
totals your ticked packages. `ui.py` is only the design and `app.py` puts the page together.
"""
        )

st.html(ui.footer())
