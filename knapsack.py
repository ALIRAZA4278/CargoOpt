"""
knapsack.py - Fractional Knapsack with the three Greedy strategies from the lecture
(Week 7 & 8: Greedy Approach).

This file is the whole "brain" of the CargoOpt project. app.py (the Streamlit
interface) only collects input and shows the result; every calculation happens here.

THE PROBLEM
    A truck can carry a limited weight (the capacity W).
    Each package has a weight and a profit.
    We want the MOST profit without going over the capacity.
    In Fractional Knapsack we may load PART of a package (for example half a sack
    of rice), so the last package can be loaded partially.

THE THREE GREEDY STRATEGIES (from the lecture)
    1. max_profit : take the package with the biggest profit first
    2. min_weight : take the lightest package first
    3. max_ratio  : take the package with the biggest profit / weight first

    Greedy means: at every step pick what looks best right now, never go back.
    Strategy 3 is the one that is proven optimal for Fractional Knapsack.

LECTURE CHECK (Example 2: profits 10,5,15,7,6,18,3  weights 2,3,5,7,1,4,1  W=15)
    max_profit = 47      min_weight = 54      max_ratio = 55.33

Run the command-line version:  python knapsack.py
"""

# strategy key -> readable name
STRATEGIES = {
    "max_profit": "Maximum profit",
    "min_weight": "Minimum weight",
    "max_ratio": "Maximum profit / weight",
}


def strategy_key(strategy, profit, weight):
    """The number the strategy sorts by (shown to the user for each step)."""
    if strategy == "max_profit":
        return profit
    if strategy == "min_weight":
        return weight
    return profit / weight   # max_ratio


def choose_order(profits, weights, strategy):
    """STEP 1 of Greedy: decide the order in which packages will be tried."""
    packages = range(len(profits))

    if strategy == "max_profit":      # biggest profit first
        return sorted(packages, key=lambda i: profits[i], reverse=True)
    if strategy == "min_weight":      # lightest first
        return sorted(packages, key=lambda i: weights[i])
    if strategy == "max_ratio":       # best profit per unit weight first
        return sorted(packages, key=lambda i: profits[i] / weights[i], reverse=True)

    raise ValueError("Unknown strategy: " + str(strategy))


def fractional_knapsack(profits, weights, capacity, strategy):
    """Fills the truck greedily. Returns the total profit and every step taken."""
    order = choose_order(profits, weights, strategy)

    remaining = capacity     # free space left in the truck
    total_profit = 0.0
    steps = []

    # STEP 2 of Greedy: go through the packages in that order
    for i in order:
        if remaining <= 1e-9:            # truck is full, stop
            break

        # Load the whole package if it fits, otherwise only the part that fits.
        weight_taken = min(weights[i], remaining)
        fraction = weight_taken / weights[i]          # 1.0 = whole package
        profit_gained = profits[i] * fraction         # profit grows with the part loaded

        remaining -= weight_taken
        total_profit += profit_gained

        steps.append({
            "item": i,                                # package number (starts at 0)
            "key": strategy_key(strategy, profits[i], weights[i]),
            "fraction": round(fraction, 6),
            "weight_taken": round(weight_taken, 6),
            "profit_gained": round(profit_gained, 6),
            "remaining": round(max(remaining, 0.0), 6),
        })

    return {
        "total_profit": round(total_profit, 4),
        "total_weight": round(capacity - max(remaining, 0.0), 4),
        "steps": steps,
    }


def check_input(profits, weights, capacity):
    """Rejects input that makes no sense, with a clear message."""
    if len(profits) == 0:
        raise ValueError("Add at least one package.")
    if len(profits) != len(weights):
        raise ValueError("Every package needs both a weight and a profit.")
    if capacity <= 0:
        raise ValueError("Truck capacity must be greater than 0.")
    if any(w <= 0 for w in weights):
        raise ValueError("Package weights must be greater than 0.")
    if any(p < 0 for p in profits):
        raise ValueError("Package profits cannot be negative.")


def compare_all(profits, weights, capacity):
    """Runs all three strategies and says which one earned the most."""
    check_input(profits, weights, capacity)

    results = {}
    for strategy in STRATEGIES:
        results[strategy] = fractional_knapsack(profits, weights, capacity, strategy)

    top = max(r["total_profit"] for r in results.values())
    best = [s for s, r in results.items() if abs(r["total_profit"] - top) < 1e-9]
    return {"strategies": results, "best": best}


def manual_load(profits, weights, capacity, chosen):
    """The packages the user ticked by hand ("Your load"): whole packages only, in list order."""
    total_weight = sum(weights[i] for i in chosen)
    if total_weight > capacity + 1e-9:
        raise ValueError(
            f"Your ticked packages weigh {total_weight:g}, which is {total_weight - capacity:g} "
            f"more than the truck capacity of {capacity:g}. Untick some packages."
        )

    remaining = capacity
    total_profit = 0.0
    steps = []
    for i in chosen:
        remaining -= weights[i]
        total_profit += profits[i]
        steps.append({
            "item": i,
            "key": profits[i],
            "fraction": 1.0,
            "weight_taken": round(weights[i], 6),
            "profit_gained": round(profits[i], 6),
            "remaining": round(max(remaining, 0.0), 6),
        })

    return {
        "total_profit": round(total_profit, 4),
        "total_weight": round(capacity - max(remaining, 0.0), 4),
        "steps": steps,
    }


# =====================================================================
# Command-line program:  python knapsack.py
# =====================================================================
def show(names, profits, weights, capacity):
    """Prints all three strategies step by step, like the lecture slides."""
    answer = compare_all(profits, weights, capacity)

    for strategy, label in STRATEGIES.items():
        result = answer["strategies"][strategy]
        print(f"\n{label}")
        for number, step in enumerate(result["steps"], start=1):
            i = step["item"]
            part = "whole" if step["fraction"] >= 0.999999 else f"{step['fraction']:.0%} of it"
            print(f"  Step {number}: {names[i]} (profit {profits[i]:g}, weight {weights[i]:g})"
                  f" -> take {part}, +{step['profit_gained']:.2f}, space left {step['remaining']:g}")
        print(f"  Total profit = {result['total_profit']:.2f}")

    winners = ", ".join(STRATEGIES[s] for s in answer["best"])
    print(f"\nBest: {winners}")


def read_number(prompt, minimum_exclusive=None):
    while True:
        try:
            value = float(input(prompt))
            if minimum_exclusive is None or value > minimum_exclusive:
                return value
        except ValueError:
            pass
        print("  Please enter a valid number.")


def enter_own():
    capacity = read_number("Truck capacity: ", 0)
    count = int(read_number("Number of packages: ", 0))
    names, profits, weights = [], [], []
    for number in range(1, count + 1):
        names.append(input(f"Package {number} name: ").strip() or f"Package {number}")
        weights.append(read_number("  weight: ", 0))
        profits.append(read_number("  profit: ", -1))
    show(names, profits, weights, capacity)


def lecture_examples():
    names = [f"Item {n}" for n in range(1, 8)]

    print("=== Lecture Example 1 (n=7, W=15) ===")
    show(names, [5, 10, 15, 7, 8, 9, 4], [1, 3, 5, 4, 1, 3, 2], 15)

    print("\n=== Lecture Example 2 (n=7, W=15) ===")
    print("Slide answer: 47, 54, 55.33")
    show(names, [10, 5, 15, 7, 6, 18, 3], [2, 3, 5, 7, 1, 4, 1], 15)


if __name__ == "__main__":
    while True:
        print("\n1) Lecture examples\n2) Enter my own packages\n3) Exit")
        choice = input("Choose 1-3: ").strip()
        if choice == "1":
            lecture_examples()
        elif choice == "2":
            enter_own()
        elif choice == "3":
            break
