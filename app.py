"""
app.py - CargoOpt page (Streamlit, Python).

IMPORTANT: this file does NO Knapsack calculation.
  knapsack.py -> all the Knapsack logic (Greedy strategies, your own load)
  ui.py       -> our design (cards, truck drawing, rows, comparison)
  app.py      -> puts the page together: reads input, calls knapsack.py, shows the result with ui.py

The "Loading sequence" is also the package list: every row has a checkbox (load it yourself),
editable name / weight / profit, the result of the selected strategy and a delete button.

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
    "manual": ("Your load", "Your load", "The packages you ticked, in that order (the last one can be loaded partly)"),
}
MAX_PACKAGES = 60


# ---------------------------------------------------------------------------
# State: the packages are a list of dicts; each row's widgets are keyed by the package id
# ---------------------------------------------------------------------------
def new_id():
    st.session_state.next_id += 1
    return st.session_state.next_id


def make_items(name):
    s = SAMPLES[name]
    return [{"id": new_id(), "name": n, "weight": float(w), "profit": float(p), "load": False, "seq": 0}
            for n, w, p in zip(s["names"], s["weights"], s["profits"])]


if "pkgs" not in st.session_state:
    first = "Lecture Example 2 (n=7, W=15)"
    st.session_state.next_id = 0
    st.session_state.pkgs = make_items(first)
    st.session_state.capacity = SAMPLES[first]["capacity"]
    st.session_state.dataset = first
    st.session_state.strategy = "max_ratio"

if st.session_state.get("strategy") is None:            # clicking the selected strategy again un-selects it
    st.session_state.strategy = st.session_state.get("last_strategy", "max_ratio")
st.session_state.last_strategy = st.session_state.strategy

for text, icon in st.session_state.pop("messages", []):
    st.toast(text, icon=icon)


def say(text, icon="⚠️"):
    st.session_state.setdefault("messages", []).append((text, icon))


def find(item_id):
    return next(it for it in st.session_state.pkgs if it["id"] == item_id)


def ticked_weight():
    return sum(it["weight"] for it in st.session_state.pkgs if it["load"])


# ----- callbacks (run before the page is drawn again) -----
def on_dataset():
    st.session_state.pkgs = make_items(st.session_state.dataset)
    st.session_state.capacity = SAMPLES[st.session_state.dataset]["capacity"]


def on_tick(item_id):
    """Your load works like Fractional Knapsack: a package that doesn't fully fit is loaded partly."""
    it = find(item_id)
    ticked = st.session_state[f"ld_{item_id}"]
    if ticked:
        free = st.session_state.capacity - ticked_weight()
        if free <= 1e-9:
            st.session_state[f"ld_{item_id}"] = False
            say("The truck is full: untick a package first")
            return
        it["seq"] = new_id()                      # remembers the order you ticked in
        if it["weight"] > free + 1e-9:
            part = round(free / it["weight"] * 100)
            say(f'Only {free:g} {st.session_state.get("unit", "kg")} free: {part}% of "{it["name"]}" is loaded', "✂️")
    it["load"] = ticked


def on_edit(item_id, field):
    it = find(item_id)
    key = {"name": "nm", "weight": "wt", "profit": "pf"}[field] + f"_{item_id}"
    value = st.session_state[key]
    if field == "name":
        value = (value or "").strip()
        if not value:
            st.session_state[key] = it["name"]
            return say("Name cannot be empty")
    elif value is None or (field == "weight" and value <= 0) or value < 0:
        st.session_state[key] = it[field]
        return say("Weight must be greater than 0" if field == "weight" else "Profit must be 0 or more")
    it[field] = value


def on_delete(item_id):
    st.session_state.pkgs = [it for it in st.session_state.pkgs if it["id"] != item_id]
    for prefix in ("ld", "nm", "wt", "pf"):
        st.session_state.pop(f"{prefix}_{item_id}", None)


def on_add():
    name = (st.session_state.f_name or "").strip()
    weight, profit = st.session_state.f_weight, st.session_state.f_profit
    error = ("Enter a package name." if not name
             else "Weight must be greater than 0." if weight is None or weight <= 0
             else "Profit must be 0 or more." if profit is None or profit < 0
             else f"Limit of {MAX_PACKAGES} packages reached." if len(st.session_state.pkgs) >= MAX_PACKAGES
             else "")
    st.session_state.form_error = error
    if error:
        return
    st.session_state.pkgs.append({"id": new_id(), "name": name, "weight": float(weight), "profit": float(profit), "load": False, "seq": 0})
    st.session_state.f_name, st.session_state.f_weight, st.session_state.f_profit = "", None, None
    say(f'Added "{name}"', "✅")


# ---------------------------------------------------------------------------
# Layout: left = setup + add form, right = results
# ---------------------------------------------------------------------------
left, right = st.columns([1, 1.9], gap="medium")

with left:
    with st.container(key="card_setup"):
        st.html(ui.card_head("Shipment", "Pick a dataset or build your own."))
        st.selectbox("Dataset", list(SAMPLES), key="dataset", on_change=on_dataset)
        note_slot = st.empty()
        c_cap, c_unit, c_cur = st.columns([1.3, 1, 1])
        c_cap.number_input("Capacity", min_value=0.0, step=1.0, key="capacity")
        unit = c_unit.selectbox("Unit", ["kg", "lb", "ton"], key="unit")
        currency = c_cur.selectbox("Currency", ["$", "Rs", "€", "£"])

    with st.container(key="card_add"):
        st.html(ui.card_head("Add package", "Name, weight and profit of one package."))
        with st.form("add_form", border=False):
            st.text_input("Name", key="f_name", max_chars=40, placeholder="e.g. Rice sacks")
            c_w, c_p = st.columns(2)
            c_w.number_input(f"Weight ({unit})", min_value=0.0, step=1.0, value=None, key="f_weight", placeholder="0")
            c_p.number_input(f"Profit ({currency})", min_value=0.0, step=1.0, value=None, key="f_profit", placeholder="0")
            st.form_submit_button("＋ Add package", type="primary", width="stretch", on_click=on_add)
        if st.session_state.get("form_error"):
            st.error(st.session_state.form_error)

capacity = float(st.session_state.capacity)
items = st.session_state.pkgs


def num(value):
    text = f"{value:,.2f}"
    return text[:-3] if text.endswith(".00") else text


def money(value):
    return f"{currency}{' ' if len(currency) > 1 else ''}{num(value)}"


def wt(value):
    return f"{num(value)} {unit}"


sample = SAMPLES.get(st.session_state.dataset, {})
untouched = ([(it["name"], it["weight"], it["profit"]) for it in items]
             == [(n, float(w), float(p)) for n, w, p in zip(sample.get("names", []), sample.get("weights", []), sample.get("profits", []))])
if sample.get("note") and untouched and capacity == sample["capacity"]:
    note_slot.html(ui.callout(sample["note"]))

# ---------------------------------------------------------------------------
# Ask knapsack.py for the answers
# ---------------------------------------------------------------------------
names = [it["name"] for it in items]
weights = [it["weight"] for it in items]
profits = [it["profit"] for it in items]
picked = [(it.get("seq", 0), i) for i, it in enumerate(items) if it["load"]]
picked.sort()                                    # in the order the user ticked them
chosen = [i for seq, i in picked]

answer, manual = None, None
if items and capacity > 0:
    answer = compare_all(profits, weights, capacity)              # the three Greedy strategies
    manual = manual_load(profits, weights, capacity, chosen)       # "Your load"

results = dict(answer["strategies"]) if answer else {}
if manual and manual["steps"]:
    results["manual"] = manual
best_profit = max((answer["strategies"][k]["total_profit"] for k in STRATEGIES), default=0.0) if answer else 0.0


def option_label(key):
    short = PLANS[key][0]                       # two lines: name, then profit in bold
    if key not in results:
        return f"{short}  \n**–**"
    star = " ★" if answer and key in answer["best"] else ""
    return f"{short}{star}  \n**{money(results[key]['total_profit'])}**"


def sort_text(key, step):
    if key == "max_profit":
        return f"profit {money(step['key'])}"
    if key == "min_weight":
        return f"weight {wt(step['key'])}"
    if key == "max_ratio":
        return f"profit/weight {step['key']:.2f}"
    return "your pick"


# ---------------------------------------------------------------------------
# Load plan card (with the editable loading sequence)
# ---------------------------------------------------------------------------
with right:
    with st.container(key="card_plan"):
        head_col, export_col = st.columns([3, 1], vertical_alignment="center")
        head_col.html(ui.card_head("Load plan", "Tick, edit or remove packages right in the loading sequence."))
        st.segmented_control("Strategy", list(PLANS), key="strategy", format_func=option_label,
                             label_visibility="collapsed", width="stretch")
        key = st.session_state.strategy or "max_ratio"
        short, full_name, rule = PLANS[key]
        st.html(f'<p class="rule">{full_name}: {rule.lower()}.</p>')

        plan = results.get(key)
        if not items:
            st.html(ui.empty("No packages yet", "Add one with the Add package form."))
        elif capacity <= 0:
            st.html(ui.empty("Truck capacity is 0", "Set a capacity greater than 0 in Shipment."))
        elif key == "manual" and not chosen:
            st.html(ui.callout("Tick packages in the loading sequence below to build your own load, "
                               "then compare it with the Greedy strategies. If a package doesn't fully fit, "
                               "only the part that fits is loaded, with profit for that part."))
        if plan:
            gap = best_profit - plan["total_profit"]
            st.html(ui.stats(
                money(plan["total_profit"]),
                "Best" if gap < 1e-9 else f"−{money(gap)} vs best", gap < 1e-9,
                num(plan["total_weight"]), wt(capacity),
                f"{round(plan['total_weight'] / capacity * 100)}%"))
            st.html(ui.truck(plan["steps"], capacity, wt(capacity)))
            csv = pd.DataFrame([{
                "Step": n, "Package": names[s["item"]], "Percent loaded": round(s["fraction"] * 100, 1),
                f"Weight loaded ({unit})": s["weight_taken"], f"Profit added ({currency})": s["profit_gained"],
                f"Space left ({unit})": s["remaining"],
            } for n, s in enumerate(plan["steps"], start=1)]).to_csv(index=False).encode("utf-8")
            export_col.download_button("⬇ Export", csv, file_name=f"cargo-plan-{key}.csv", mime="text/csv", width="stretch")

        # ----- the loading sequence = the package list -----
        if items:
            steps = {s["item"]: (n, s) for n, s in enumerate(plan["steps"], start=1)} if plan else {}
            order = [s["item"] for s in plan["steps"]] if plan else []
            order += [i for i in range(len(items)) if i not in steps]      # not loaded: at the end

            st.html(ui.sequence_head(len(steps), len(items)))
            widths = [0.35, 0.45, 2.2, 1.05, 1.05, 2.3, 0.4]
            with st.container(key="seq"):
                with st.container(key="seqhead"):
                    head = st.columns(widths, vertical_alignment="bottom", gap="small")
                    for col, text in zip(head, ["", "#", "Package", f"Weight ({unit})", f"Profit ({currency})",
                                                "Your load" if key == "manual" else "Greedy load", ""]):
                        col.html(ui.header_cell(text))
                for i in order:
                    it = items[i]
                    pid = it["id"]
                    # first time a row is drawn: put the package values into its widgets
                    for prefix, value in (("ld", it["load"]), ("nm", it["name"]), ("wt", it["weight"]), ("pf", it["profit"])):
                        st.session_state.setdefault(f"{prefix}_{pid}", value)
                    with st.container(key=f"row_{pid}"):
                        c = st.columns(widths, vertical_alignment="center", gap="small")
                        c[0].checkbox("Load", key=f"ld_{pid}", on_change=on_tick, args=(pid,), label_visibility="collapsed",
                                      help="Load this package yourself (Your load)")
                        c[1].html(ui.node(i))
                        c[2].text_input("Name", key=f"nm_{pid}", max_chars=40, on_change=on_edit, args=(pid, "name"),
                                        label_visibility="collapsed")
                        c[3].number_input(f"Weight ({unit})", key=f"wt_{pid}", min_value=0.0, step=1.0, format="%g",
                                          on_change=on_edit, args=(pid, "weight"))
                        c[4].number_input(f"Profit ({currency})", key=f"pf_{pid}", min_value=0.0, step=1.0, format="%g",
                                          on_change=on_edit, args=(pid, "profit"))
                        if i in steps:
                            n, s = steps[i]
                            c[5].html(ui.step_result(n, s["fraction"], f"{sort_text(key, s)} · {wt(s['remaining'])} left",
                                                     money(s["profit_gained"])))
                        else:
                            if key != "manual":
                                c[5].html(ui.not_loaded("Not loaded"))
                            else:
                                c[5].html(ui.not_loaded("Ticked · no space left" if it["load"] else "Not ticked"))
                        c[6].button(":material/delete:", key=f"del_{pid}", on_click=on_delete, args=(pid,),
                                    help=f"Remove {it['name']}")

            st.html(ui.load_footer(
                len(chosen), wt(manual["total_weight"] if manual else 0), wt(capacity),
                money(manual["total_profit"]) if manual else "-",
                wt(max(0.0, capacity - (manual["total_weight"] if manual else 0)))))

    # -----------------------------------------------------------------------
    # Strategy comparison card
    # -----------------------------------------------------------------------
    with st.container(key="card_compare"):
        st.html(ui.card_head("Strategy comparison", "Total profit of each Greedy rule on the same shipment."))
        if not answer:
            st.html('<p class="rule">The comparison appears once there are packages to load.</p>')
        else:
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
                        "is always optimal. Tick packages in the loading sequence to try to beat it yourself.")
            st.html(ui.callout(note))

    # -----------------------------------------------------------------------
    # How it works
    # -----------------------------------------------------------------------
    with st.container(key="card_about"):
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
