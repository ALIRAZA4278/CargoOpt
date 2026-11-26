"""
knapsack.py - Fractional Knapsack with 3 Greedy strategies (Week 7 & 8).

    max_profit : biggest profit first
    min_weight : lightest package first
    max_ratio  : biggest profit / weight first  (best for Fractional Knapsack)

Lecture Example 2 answer: 47, 54, 55.33
Run:  python knapsack.py
"""

# ---------------- 1. The three strategies ----------------
STRATEGIES = {
    "max_profit": "Maximum profit",
    "min_weight": "Minimum weight",
    "max_ratio": "Maximum profit / weight",
}


# ---------------- 2. Small helpers ----------------
def strategy_key(strategy, profit, weight):
    """The number each strategy sorts by."""
    if strategy == "max_profit":
        return profit
    if strategy == "min_weight":
        return weight
    return profit / weight


def add_step(steps, i, key, fraction, weight, profit, remaining):
    """Saves one loading step in the list."""
    steps.append({"item": i, "key": key, "fraction": round(fraction, 6),
                  "weight_taken": round(weight, 6), "profit_gained": round(profit, 6),
                  "remaining": round(max(remaining, 0), 6)})


def make_result(capacity, remaining, total, steps):
    """The final answer: total profit, total weight loaded, and all steps."""
    return {"total_profit": round(total, 4),
            "total_weight": round(capacity - max(remaining, 0), 4),
            "steps": steps}


# ---------------- 3. Greedy algorithm ----------------
def choose_order(profits, weights, strategy):
    """Greedy step 1: put the packages in order, best first."""
    pairs = []
    for i in range(len(profits)):
        key = strategy_key(strategy, profits[i], weights[i])
        if strategy != "min_weight":
            key = -key                  # minus sign = biggest first
        pairs.append((key, i))
    pairs.sort()
    return [i for key, i in pairs]


def fractional_knapsack(profits, weights, capacity, strategy):
    """Greedy step 2: load in that order; the last package may be loaded partly."""
    remaining, total, steps = capacity, 0.0, []
    for i in choose_order(profits, weights, strategy):
        if remaining <= 1e-9:           # truck is full
            break
        weight = min(weights[i], remaining)
        fraction = weight / weights[i]
        profit = profits[i] * fraction
        remaining -= weight
        total += profit
        add_step(steps, i, strategy_key(strategy, profits[i], weights[i]),
                 fraction, weight, profit, remaining)
    return make_result(capacity, remaining, total, steps)


# ---------------- 4. Compare all three strategies ----------------
def compare_all(profits, weights, capacity):
    """Runs all 3 strategies and says which one is best."""
    if not profits or len(profits) != len(weights):
        raise ValueError("Every package needs a weight and a profit.")
    if capacity <= 0 or min(weights) <= 0 or min(profits) < 0:
        raise ValueError("Capacity and weights must be above 0, profits cannot be negative.")

    results = {}
    for s in STRATEGIES:
        results[s] = fractional_knapsack(profits, weights, capacity, s)
    top = max(r["total_profit"] for r in results.values())
    best = [s for s in results if abs(results[s]["total_profit"] - top) < 1e-9]
    return {"strategies": results, "best": best}


# ---------------- 5. The user's own load ("Your load") ----------------
def manual_load(profits, weights, capacity, chosen):
    """The packages the user ticked, in the order ticked; the last one may be loaded partly."""
    remaining, total, steps = capacity, 0.0, []
    for i in chosen:
        if remaining <= 1e-9:           # truck is full
            break
        weight = min(weights[i], remaining)
        fraction = weight / weights[i]
        profit = profits[i] * fraction
        remaining -= weight
        total += profit
        add_step(steps, i, profits[i], fraction, weight, profit, remaining)
    return make_result(capacity, remaining, total, steps)


# ---------------- 6. Command-line version ----------------
def show(profits, weights, capacity):
    """Prints every step of all 3 strategies."""
    answer = compare_all(profits, weights, capacity)
    for s, label in STRATEGIES.items():
        print(f"\n{label}")
        for step in answer["strategies"][s]["steps"]:
            print(f"  Item {step['item'] + 1}: take {step['fraction']:.0%}, "
                  f"+{step['profit_gained']:.2f}, space left {step['remaining']:g}")
        print(f"  Total profit = {answer['strategies'][s]['total_profit']:.2f}")
    print("\nBest:", ", ".join(STRATEGIES[s] for s in answer["best"]))


if __name__ == "__main__":
    print("=== Lecture Example 1 (W=15) ===")
    show([5, 10, 15, 7, 8, 9, 4], [1, 3, 5, 4, 1, 3, 2], 15)
    print("\n=== Lecture Example 2 (W=15), slide answer 47, 54, 55.33 ===")
    show([10, 5, 15, 7, 6, 18, 3], [2, 3, 5, 7, 1, 4, 1], 15)
