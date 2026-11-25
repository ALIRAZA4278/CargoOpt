# `knapsack.py` – Line by line explanation

`knapsack.py` CargoOpt ka dimaag hai: saari calculation yahin hoti hai. File **6 sections** mein hai, aur woh usi order mein hain jis order mein cheezein ek doosre ko use karti hain:

```
1. STRATEGIES ─────────────────────────────┐
2. strategy_key, add_step, make_result     │  (helpers)
3. choose_order → fractional_knapsack      │  (Greedy algorithm)
4. compare_all  ── teeno strategies chalata hai (1 + 3 use karta hai)
5. manual_load  ── user ka apna load (2 use karta hai)
6. show + __main__ ── command line par print (4 use karta hai)
```

**Function kaun kisay call karta hai:**

```
compare_all()
   └── fractional_knapsack()      (har strategy ke liye ek baar, total 3 baar)
          ├── choose_order()
          │      └── strategy_key()
          ├── strategy_key()
          ├── add_step()
          └── make_result()

manual_load()
   ├── add_step()
   └── make_result()

app.py  →  compare_all()  aur  manual_load()   (sirf yeh do + STRATEGIES)
```

Is document mein hum ek example saath saath chalayenge, **Lecture Example 2**:

| Package (i) | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Naam | Item 1 | Item 2 | Item 3 | Item 4 | Item 5 | Item 6 | Item 7 |
| profit | 10 | 5 | 15 | 7 | 6 | 18 | 3 |
| weight | 2 | 3 | 5 | 7 | 1 | 4 | 1 |

Capacity `W = 15`. Note: Python mein numbering **0 se** shuru hoti hai, is liye "Item 1" ka index `i = 0` hai.

---

## Lines 1–10: Docstring (file ka introduction)

```python
"""
knapsack.py - Fractional Knapsack with 3 Greedy strategies (Week 7 & 8).
    max_profit : biggest profit first
    ...
Lecture Example 2 answer: 47, 54, 55.33
Run:  python knapsack.py
"""
```

- `"""` se `"""` tak ka text **docstring** hai. Python isay chalata nahi, yeh sirf parhne wale ke liye note hai.
- Batata hai file kya karti hai, teeno strategies kya hain, lecture ka sahi answer kya hai, aur file kaise chalani hai.

---

## Section 1 – Lines 12–17: `STRATEGIES`

```python
STRATEGIES = {
    "max_profit": "Maximum profit",
    "min_weight": "Minimum weight",
    "max_ratio": "Maximum profit / weight",
}
```

- **Line 12:** `#` wali line comment hai, sirf section ka naam.
- **Line 13:** `STRATEGIES` ek **dictionary** hai (key → value). Capital letters ka matlab: yeh constant hai, badalta nahi.
- **Lines 14–16:** baayein taraf **key** hai (code mein use hoti hai, jaise `"max_ratio"`), daayein taraf **readable naam** (user ko dikhta hai).
- **Connection:**
  - `compare_all()` (line 82) isi par loop chala kar teeno strategies chalata hai.
  - `show()` (line 108) isi se naam print karta hai.
  - `app.py` bhi isay import karta hai.
  - Nayi strategy add karni ho to yahan ek line aur `strategy_key()` mein ek `if` add karna kaafi hai.

---

## Section 2 – Small helpers

### Lines 21–27: `strategy_key()`

```python
def strategy_key(strategy, profit, weight):
    """The number each strategy sorts by."""
    if strategy == "max_profit":
        return profit
    if strategy == "min_weight":
        return weight
    return profit / weight
```

- **Line 21:** `def` se function banta hai. Yeh 3 cheezein leta hai: strategy ka naam, ek package ka profit, aur us ka weight.
- **Line 22:** docstring, function kya karta hai.
- **Lines 23–24:** agar strategy `"max_profit"` hai to package ko **profit** se judge karo.
- **Lines 25–26:** agar `"min_weight"` hai to **weight** se.
- **Line 27:** baaqi bacha `"max_ratio"`, to **profit ÷ weight** (har kg ka profit).
- `return` milte hi function wahin ruk jaata hai, is liye `else` likhne ki zaroorat nahi.
- **Example:** Item 1 (profit 10, weight 2): max_profit → `10`, min_weight → `2`, max_ratio → `10/2 = 5.0`.
- **Connection:** `choose_order()` (line 49) isi se sort karta hai, aur `fractional_knapsack()` (line 68) yahi number har step mein save karta hai, taake `app.py` dikha sake (jaise "profit/weight 5.00").

### Lines 30–34: `add_step()`

```python
def add_step(steps, i, key, fraction, weight, profit, remaining):
    """Saves one loading step in the list."""
    steps.append({"item": i, "key": key, "fraction": round(fraction, 6),
                  "weight_taken": round(weight, 6), "profit_gained": round(profit, 6),
                  "remaining": round(max(remaining, 0), 6)})
```

- **Line 30:** ek loading step ki saari info leta hai, aur `steps` woh list hai jis mein step add karna hai.
- **Line 32:** `steps.append({...})` list ke aakhir mein ek naya **dictionary** jorta hai. Har step mein yeh hota hai:

| Key | Matlab |
|---|---|
| `"item"` | package ka index (0 se) |
| `"key"` | strategy ka number (strategy_key se) |
| `"fraction"` | package ka kitna hissa load hua (1.0 = poora, 0.5 = aadha) |
| `"weight_taken"` | kitna weight load hua |
| `"profit_gained"` | is step se kitna profit mila |
| `"remaining"` | is step ke baad truck mein kitni jagah bachi |

- `round(x, 6)`: number ko 6 decimal tak gol kar deta hai, taake `0.6666666666666666` jaisi lambi values na aayein.
- `max(remaining, 0)`: computer ke decimal hisaab mein kabhi kabhi `-0.0000000001` aa jaata hai. `max(..., 0)` isay 0 kar deta hai, kyunke jagah negative nahi ho sakti.
- **Kyun banaya:** yahi dictionary `fractional_knapsack()` aur `manual_load()` dono banate hain. Ek helper bana kar code do baar nahi likhna para.
- **Connection:** `app.py` aur `ui.py` yahi keys parhte hain: `ui.truck()` `item`, `weight_taken` aur `fraction` se blocks banata hai, Loading sequence `fraction`, `key`, `remaining` aur `profit_gained` dikhata hai, aur CSV export bhi inhi se banta hai. **Is liye in keys ke naam badalne se app toot jaayegi.**

### Lines 37–41: `make_result()`

```python
def make_result(capacity, remaining, total, steps):
    """The final answer: total profit, total weight loaded, and all steps."""
    return {"total_profit": round(total, 4),
            "total_weight": round(capacity - max(remaining, 0), 4),
            "steps": steps}
```

- Final answer ek dictionary mein wapas karta hai:
  - `"total_profit"`: kul profit, 4 decimal tak.
  - `"total_weight"`: kitna weight load hua = capacity − bachi hui jagah. Example: 15 − 0 = 15.
  - `"steps"`: saare steps ki list (add_step se bani).
- **Kyun banaya:** `fractional_knapsack()` aur `manual_load()` dono ka answer ek hi shape ka hai, is liye ek helper.
- **Connection:** `app.py` `total_profit` se stats aur comparison bars, aur `total_weight` se "Loaded" aur "Utilization %" dikhata hai.

---

## Section 3 – Greedy algorithm

Greedy ka matlab: **har qadam par jo abhi sab se acha lage woh utha lo, wapas mur kar mat dekho.** Is ke 2 steps hain:

1. Packages ko order mein lagao (`choose_order`)
2. Us order mein truck bharo (`fractional_knapsack`)

### Lines 45–54: `choose_order()` – Greedy step 1

```python
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
```

- **Line 45:** saare profits, saare weights (lists) aur strategy leta hai.
- **Line 47:** `pairs = []` ek khaali list.
- **Line 48:** `range(len(profits))` = 0, 1, 2, ... (jitne packages hain). Har package `i` ke liye loop.
- **Line 49:** us package ka sort number nikalo (`strategy_key` se).
- **Lines 50–51:** `sort()` hamesha **chhote se bare** (ascending) karta hai.
  - `min_weight` ko chhota pehle chahiye, to number waisa hi rehta hai.
  - `max_profit` aur `max_ratio` ko **bara pehle** chahiye. Number ko **minus** kar do to sab se bara number sab se chhota ban jaata hai (18 → −18) aur sort mein pehle aa jaata hai.
- **Line 52:** `(key, i)` ek **tuple** (jora): pehle sort number, phir package ka index.
- **Line 53:** `pairs.sort()` tuples ko sort karta hai. Python pehle **pehli value** (key) compare karta hai; agar woh barabar ho (tie), to **doosri value** (i) se. Is liye tie mein chhota package number pehle aata hai. **Is ke liye `lambda` ki zaroorat nahi pari.**
- **Line 54:** `[i for key, i in pairs]` ek **list comprehension** hai: har jore se sirf `i` nikaal kar nayi list. Yehi final order hai.

**Example (max_ratio):**

| i | profit/weight | key (minus) |
|---|---|---|
| 0 | 10/2 = 5 | −5 |
| 1 | 5/3 = 1.67 | −1.67 |
| 2 | 15/5 = 3 | −3 |
| 3 | 7/7 = 1 | −1 |
| 4 | 6/1 = 6 | −6 |
| 5 | 18/4 = 4.5 | −4.5 |
| 6 | 3/1 = 3 | −3 |

Sort ke baad: `(−6,4) (−5,0) (−4.5,5) (−3,2) (−3,6) (−1.67,1) (−1,3)`

Order = `[4, 0, 5, 2, 6, 1, 3]`, yaani Item 5, Item 1, Item 6, Item 3, Item 7, Item 2, Item 4.
(Item 3 aur Item 7 dono ka ratio 3 hai; tie mein `i = 2` pehle aaya kyunke 2 < 6.)

**Connection:** sirf `fractional_knapsack()` (line 60) isay call karta hai.

### Lines 57–70: `fractional_knapsack()` – Greedy step 2

```python
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
```

- **Line 59:** teen variables ek saath:
  - `remaining = capacity`: truck mein kitni jagah khaali hai (shuru mein poori, 15).
  - `total = 0.0`: ab tak ka profit.
  - `steps = []`: steps ki list.
- **Line 60:** `choose_order()` se order lo aur us order mein har package `i` par chalo.
- **Lines 61–62:** agar jagah khatam ho gayi to `break` (loop band). `1e-9` = 0.000000001: decimal numbers mein bilkul 0 nahi aata, is liye "almost 0" check karte hain.
- **Line 63:** `min(package ka weight, bachi jagah)`:
  - package fit ho jaaye to poora weight,
  - fit na ho to sirf utna jitni jagah bachi hai. **Yahi "fractional" wala hissa hai.**
- **Line 64:** `fraction` = kitna hissa load hua. Poora = `1.0`, jaise 2 mein se 2 → 1.0, aur 3 mein se 2 → 0.667.
- **Line 65:** profit bhi usi hisse ke hisaab se: aadha package = aadha profit.
- **Line 66:** `remaining -= weight` yaani `remaining = remaining - weight`, jagah kam karo.
- **Line 67:** `total += profit`, profit jor do.
- **Lines 68–69:** yeh step `add_step()` se list mein save karo.
- **Line 70:** `make_result()` se final answer wapas karo.

**Example (max_ratio, W = 15), order `[4, 0, 5, 2, 6, 1, 3]`:**

| Step | Package | weight | Load (`weight`) | fraction | profit | remaining | total |
|---|---|---|---|---|---|---|---|
| 1 | Item 5 (i=4) | 1 | 1 | 1.0 | 6 | 14 | 6 |
| 2 | Item 1 (i=0) | 2 | 2 | 1.0 | 10 | 12 | 16 |
| 3 | Item 6 (i=5) | 4 | 4 | 1.0 | 18 | 8 | 34 |
| 4 | Item 3 (i=2) | 5 | 5 | 1.0 | 15 | 3 | 49 |
| 5 | Item 7 (i=6) | 1 | 1 | 1.0 | 3 | 2 | 52 |
| 6 | Item 2 (i=1) | 3 | **2** (min(3, 2)) | **0.667** | 5 × 0.667 = 3.33 | 0 | **55.33** |
| – | Item 4 (i=3) | | `remaining` 0 hai → `break` | | | | |

Answer **55.33**, bilkul lecture slide jaisa.

**Connection:** `compare_all()` (line 83) isay har strategy ke liye ek baar call karta hai.

---

## Section 4 – Lines 74–86: `compare_all()`

```python
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
```

- **Lines 76–77:** input check:
  - `not profits`: list khaali hai (koi package nahi).
  - `len(profits) != len(weights)`: kisi package ka weight ya profit missing hai.
  - Ghalat ho to `raise ValueError(...)`: error de kar function wahin ruk jaata hai.
- **Lines 78–79:** doosra check:
  - `capacity <= 0`: truck ki capacity 0 ya negative nahi ho sakti.
  - `min(weights) <= 0`: koi weight 0 ho to line 64 mein **0 se divide** ka error aata, is liye pehle hi rok do.
  - `min(profits) < 0`: profit negative nahi ho sakta.
- **Line 81:** `results = {}` khaali dictionary.
- **Lines 82–83:** `STRATEGIES` ki har key (`"max_profit"`, `"min_weight"`, `"max_ratio"`) ke liye `fractional_knapsack()` chalao aur answer `results` mein us key par rakho.
- **Line 84:** teeno mein se sab se bara `total_profit` = `top`. Example: max(47, 54, 55.33) = 55.33.
- **Line 85:** woh strategies jin ka profit `top` ke barabar hai. Barabar check karne ke liye `==` ki jagah `abs(a − b) < 1e-9` (farq bohat chhota hai) use kiya, kyunke decimal numbers mein `==` kabhi kabhi galat nikalta hai. **List** is liye ke do strategies ka profit barabar bhi ho sakta hai.
- **Line 86:** answer is shape mein wapas aata hai:

```python
{"strategies": {"max_profit": {...}, "min_weight": {...}, "max_ratio": {...}},
 "best": ["max_ratio"]}
```

- **Connection:** `app.py` line 225 isay call karta hai. `answer["best"]` se strategy ke saath ★ aur comparison mein "Optimal" badge lagta hai.

---

## Section 5 – Lines 90–101: `manual_load()` ("Your load")

```python
def manual_load(profits, weights, capacity, chosen):
    """The packages the user ticked by hand (whole packages only)."""
    used = sum(weights[i] for i in chosen)
    if used > capacity + 1e-9:
        raise ValueError(f"Your ticked packages weigh {used:g}, which is {used - capacity:g} more "
                         f"than the truck capacity of {capacity:g}. Untick some packages.")
    remaining, total, steps = capacity, 0.0, []
    for i in chosen:
        remaining -= weights[i]
        total += profits[i]
        add_step(steps, i, profits[i], 1.0, weights[i], profits[i], remaining)
    return make_result(capacity, remaining, total, steps)
```

- Yeh Greedy nahi hai. User app mein khud packages **tick** karta hai, aur yeh function un ka total nikalta hai, taake user apna load Greedy se compare kar sake.
- **Line 90:** `chosen` = tick kiye hue packages ke index, jaise `[0, 2, 5]`.
- **Line 92:** `sum(weights[i] for i in chosen)`: tick kiye packages ka kul weight.
- **Lines 93–95:** zyada weight ho to error. Message **f-string** hai (`f"..."`): `{used:g}` ki jagah value aa jaati hai. `:g` ka matlab number ko saaf dikhao, `15.0` ki jagah `15`.
- **Line 96:** shuruaati values, `fractional_knapsack()` jaisi.
- **Lines 97–99:** har ticked package **poora** load hota hai (koi hissa nahi), to jagah kam karo aur profit jor do.
- **Line 100:** step save karo. `fraction` hamesha `1.0` (poora), aur `key` ki jagah profit.
- **Line 101:** `make_result()` se answer.
- **Connection:** `app.py` line 227 isay `try/except` ke andar call karta hai. Agar `ValueError` aaye to error ka message "Your load" mein laal box mein dikhta hai.

---

## Section 6 – Lines 105–121: Command-line version

### Lines 105–114: `show()`

```python
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
```

- **Line 107:** `compare_all()` se teeno answers lo.
- **Line 108:** `.items()` se key aur naam dono ek saath milte hain, jaise `("max_ratio", "Maximum profit / weight")`.
- **Line 109:** strategy ka naam print karo. `\n` = nayi line.
- **Lines 110–112:** har step print karo:
  - `step['item'] + 1`: index 0 se shuru hota hai, user ke liye 1 se dikhao.
  - `:.0%`: fraction ko percent mein, jaise `0.667` → `67%` aur `1.0` → `100%`.
  - `:.2f`: 2 decimal tak, jaise `3.33`.
- **Line 113:** total profit print.
- **Line 114:** `", ".join(...)`: best strategies ke naam comma se jor kar print.

### Lines 117–121: `if __name__ == "__main__":`

```python
if __name__ == "__main__":
    print("=== Lecture Example 1 (W=15) ===")
    show([5, 10, 15, 7, 8, 9, 4], [1, 3, 5, 4, 1, 3, 2], 15)
    print("\n=== Lecture Example 2 (W=15), slide answer 47, 54, 55.33 ===")
    show([10, 5, 15, 7, 6, 18, 3], [2, 3, 5, 7, 1, 4, 1], 15)
```

- **Line 117:** yeh hissa **sirf tab** chalta hai jab file seedha chalayi jaaye (`python knapsack.py`). Jab `app.py` isay `import` karta hai to yeh nahi chalta, is liye website par yeh print nahi hota.
- **Lines 118–121:** lecture ke dono examples (profits, weights, capacity 15) `show()` ko de kar print karo.

**Output (short):**

```
Lecture Example 1:  47.25,  46.00,  51.00   → Best: Maximum profit / weight
Lecture Example 2:  47.00,  54.00,  55.33   → Best: Maximum profit / weight
```

---

## Short summary (viva ke liye)

1. **Greedy** = har qadam par abhi ka best choice, wapas nahi jaana.
2. `choose_order()` packages ko strategy ke number se sort karta hai. Bara pehle chahiye to number ko minus kar dete hain, aur tie mein chhota index pehle.
3. `fractional_knapsack()` order mein package uthata hai: fit ho to poora, warna sirf bacha hua hissa (`min(weight, remaining)`), aur profit usi fraction se.
4. `compare_all()` teeno strategies chala kar best batata hai, aur **profit / weight hamesha optimal** hota hai Fractional Knapsack mein.
5. `manual_load()` user ke tick kiye hue poore packages ka total nikalta hai.
6. **Time complexity:** sorting `O(n log n)` + loading loop `O(n)` = **O(n log n)** har strategy ke liye.
7. File mein koi `import` nahi aur koi `lambda` nahi. Sirf plain Python hai.
