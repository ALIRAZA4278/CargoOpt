# CargoOpt - Truck Load Optimizer

DAA project based on the **0/1 Knapsack problem**.

A truck has a limited capacity. Each package has a weight and a profit. CargoOpt finds the combination of packages with the **maximum total profit** that fits in the truck, using **Dynamic Programming**, and compares it with Greedy strategies.

## How Knapsack is used

| Cargo project | Knapsack |
|---|---|
| Truck capacity | Knapsack capacity `W` |
| Package weight | Item weight |
| Package profit | Item value |

Each package is either loaded fully or not at all, so this is **0/1 Knapsack**.

- `knapsack.js` has the algorithms: `bruteForce` O(2^n), `greedy01` O(n log n), `dp01` O(n x W). It is fully commented.
- `cargo.js` is the UI. It calls `dp01()` and `greedy01()` from `knapsack.js`.
- DP recurrence: `dp[i][w] = max(dp[i-1][w], value[i] + dp[i-1][w - weight[i]])`

## Features

- Enter your own packages: form, editable table, bulk paste, CSV upload
- Optimize load animation, truck cargo bay visual
- Strategy comparison: manual vs Greedy vs DP
- DP table viewer with backtracking highlights
- CSV export and print report

## Run

No build step. Open `cargo.html` in a browser, or deploy the folder to Netlify.

## Files

- `cargo.html` page and styles
- `cargo.js` UI logic
- `knapsack.js` Knapsack algorithms
