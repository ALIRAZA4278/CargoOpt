# CargoOpt - Truck Load Optimizer (Python)

DAA project: **Fractional Knapsack** solved with the **three Greedy strategies** from the
Week 7 & 8 lecture (Greedy Approach). The whole project is written in Python.

| Strategy | Rule | Lecture Example 2 |
|---|---|---|
| Maximum profit | biggest profit first | 47 |
| Minimum weight | lightest package first | 54 |
| Maximum profit / weight | best profit per unit of weight first | 55.33 (optimal) |

You can also tick packages yourself ("Your load") and compare your choice with the three strategies.

## Files

| File | Job |
|---|---|
| `knapsack.py` | **All the Knapsack logic.** `choose_order()` sorts the packages, `fractional_knapsack()` fills the truck, `compare_all()` runs the three strategies, `manual_load()` totals the ticked packages. Also a command-line program. |
| `app.py` | The web interface (Streamlit). Collects input, calls `knapsack.py`, shows the results. No Knapsack calculation here. |
| `requirements.txt` | Python packages needed. |
| `.streamlit/config.toml` | Colours of the interface. |

## Run

```
pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at http://localhost:8501

Command-line version (no install needed):

```
python knapsack.py
```

## Deploy (free)

Push this folder to GitHub, then on https://share.streamlit.io choose the repository and `app.py`.
