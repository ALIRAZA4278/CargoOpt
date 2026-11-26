# CargoOpt – Har file ka explanation

CargoOpt ek web app hai jo **Fractional Knapsack** problem ko lecture (Week 7 & 8, Greedy Approach) ki **3 Greedy strategies** se solve karti hai:

| Strategy | Rule |
|---|---|
| Maximum profit | sab se zyada profit wala package pehle |
| Minimum weight | sab se halka package pehle |
| Maximum profit / weight | sab se zyada profit per kg wala pehle (yehi optimal hai) |

Truck ki ek limit (capacity) hoti hai. Fractional Knapsack mein package ka **hissa** bhi load ho sakta hai, jaise aadhi bori chawal.

---

## Project ka structure (kaun kis se connected hai)

```
                 requirements.txt  (kaun se packages install karne hain)
                         |
   .streamlit/config.toml (theme / colours)
                         |
                         v
 user ka browser  <---  app.py  (page jorta hai)
                       /      \
                      v        v
               knapsack.py    ui.py
            (saari calculation) (saara design: CSS, HTML, SVG)
```

- **app.py** user se input leta hai, **knapsack.py** se answer mangta hai, aur **ui.py** se design bana kar dikhata hai.
- **knapsack.py** aur **ui.py** ek doosre ko nahi jaante. Dono sirf app.py se connected hain.
- Is ka faida yeh hai ke algorithm (knapsack.py) design se bilkul alag hai, is liye usay akele bhi chala sakte hain: `python knapsack.py`.

---

## 1. `knapsack.py` – project ka "dimaag"

**Kaam:** saari Knapsack calculation yahan hoti hai, aur kisi file mein koi calculation nahi.

| Function | Kya karta hai |
|---|---|
| `STRATEGIES` | 3 strategies ke naam (key → readable naam) |
| `strategy_key()` | batata hai har strategy kis number se sort karti hai (profit, weight ya profit/weight) |
| `choose_order()` | Greedy step 1: packages ko best-first order mein lagata hai |
| `fractional_knapsack()` | Greedy step 2: truck ko us order mein bharta hai, aakhri package partly |
| `compare_all()` | teeno strategies chalata hai aur batata hai kaun si best hai |
| `manual_load()` | user ke tick kiye hue packages ko tick ke order mein load karta hai ("Your load"); jo poora fit na ho uska hissa |
| `show()` + `__main__` | command-line version, lecture ke dono examples print karta hai |

**Packages:** koi nahi. Yeh file **sirf plain Python** hai, koi `import` nahi. Is liye bina kuch install kiye chal jaati hai, aur teacher ko algorithm samjhana easy hai.

Poori line-by-line detail doosre document mein hai: `docs/2-knapsack-line-by-line.md`.

---

## 2. `app.py` – page jorne wali file

**Kaam:** Streamlit web page banata hai:

1. **Shipment card:** dataset chunna (Lecture Example 1/2, Bulk cargo, Start blank), capacity, unit (kg/lb/ton), currency.
2. **Add package form:** naya package (naam, weight, profit) add karna.
3. **Load plan card:** strategy select karna, profit/utilization stats, truck ki drawing, aur "Loading sequence" table jahan har package ko tick, edit ya delete kar sakte hain.
4. **Strategy comparison card:** teeno strategies + "Your load" ka profit bars mein.
5. **Export button:** load plan CSV file mein download.

**knapsack.py se connection:**

- `from knapsack import STRATEGIES, compare_all, manual_load` (line 19)
- `compare_all(profits, weights, capacity)` se teeno strategies ka answer (line 221)
- `manual_load(profits, weights, capacity, chosen)` se user ka apna load (line 222)

**ui.py se connection:** `import ui`, phir `st.html(ui.card_head(...))`, `ui.truck(...)`, `ui.comparison(...)` waghera.

### app.py ke packages

| Package | Kya kaam karta hai | Hum ne kyun use kiya |
|---|---|---|
| **streamlit** (`import streamlit as st`) | Python code se web page banata hai: buttons, inputs, checkboxes, columns, toast messages. `st.session_state` page reload hone par bhi data (packages list) yaad rakhta hai. | Hum HTML/JavaScript ka poora frontend nahi likhna chahte the. Streamlit se **sirf Python** mein interactive web app ban jaati hai, aur free deploy bhi ho jaati hai (share.streamlit.io). |
| **pandas** (`import pandas as pd`) | Tables (DataFrame) ke saath kaam karta hai. | Sirf **Export** button ke liye: load plan ke steps ko `pd.DataFrame(...)` mein daal kar `.to_csv()` se CSV file banti hai (line 278–282). |

---

## 3. `ui.py` – design (look) wali file

**Kaam:** page ka saara design. Is mein **koi calculation nahi**. Har function app.py se data leta hai aur HTML ka ek tukra (string) wapas karta hai.

| Cheez | Kya hai |
|---|---|
| `CSS` | ek lambi string jis mein saari styling hai: cards, colours, buttons, mobile layout. app.py isay `st.html(ui.CSS)` se lagata hai. |
| `PALETTE`, `color_of()` | har package ka apna colour, jo table, truck aur timeline mein same rehta hai |
| `app_bar()`, `card_head()`, `callout()`, `empty()`, `stats()` | chhote design pieces (top bar, card ka title, info box, khaali state, stats) |
| `truck()` | truck ki **SVG drawing**. Har load hua package ek coloured block hai, aur block ki width = weight / capacity. Partly load hua package striped dikhta hai. |
| `sequence_head()`, `header_cell()`, `node()`, `step_result()`, `not_loaded()` | Loading sequence table ke pieces |
| `comparison()` | strategies ki comparison bars |
| `load_footer()`, `footer()` | neeche wali lines |

### ui.py ke packages (dono Python ke built-in hain, install nahi karne parte)

| Package | Kya kaam karta hai | Hum ne kyun use kiya |
|---|---|---|
| **base64** | text/data ko base64 code mein badalta hai. | Streamlit HTML mein se `<svg>` tag hata deta hai. Is liye `svg_image()` SVG drawing ko base64 karke `<img src="data:image/svg+xml;base64,...">` ke andar daalta hai, taake truck aur icons dikh sakein. |
| **html.escape** (`from html import escape`) | `<`, `>`, `&`, `"` jaise characters ko safe bana deta hai. | User package ka naam khud likhta hai. Agar koi naam mein `<b>` ya `<script>` likh de to page kharab ho sakta hai. `escape()` se naam sirf text ki tarah dikhta hai, HTML ki tarah nahi chalta. |

---

## 4. `requirements.txt` – zaroori packages ki list

```
streamlit>=1.50
pandas>=2.2
altair>=5.4
```

`pip install -r requirements.txt` yeh sab install kar deta hai. `>=` ka matlab: kam se kam yeh version.

- **streamlit**: web app (upar dekhein)
- **pandas**: CSV export (upar dekhein)
- **altair**: charts banane wali library. **Hamara code isay directly use nahi karta.** Streamlit khud apne charts ke liye altair use karta hai aur usay khud hi install kar leta hai, is liye yeh line hata bhi sakte hain. Rakhne ka bas itna faida hai ke version pakka rehta hai.

---

## 5. `.streamlit/config.toml` – Streamlit ki settings

| Setting | Matlab |
|---|---|
| `[theme]` `primaryColor = "#0f766e"` | main teal colour (buttons, selected cheezein) |
| `backgroundColor`, `secondaryBackgroundColor`, `borderColor`, `textColor` | page, cards, borders aur text ke colours |
| `baseRadius = "10px"` | rounded corners |
| `font = "sans serif"` | font |
| `[client]` `toolbarMode = "minimal"` | Streamlit ka upar wala menu chhota |
| `[server]` `headless = true` | server bina khud browser khole chalta hai (deploy ke liye zaroori) |

Streamlit yeh file khud parhta hai, kisi Python file mein import nahi hoti.

---

## 6. `README.md`

Project ki introduction: kya hai, kaun si file kya karti hai, kaise chalana hai (`pip install -r requirements.txt` phir `python -m streamlit run app.py`), aur kaise deploy karna hai. GitHub par yehi sab se pehle dikhti hai.

## 7. `.gitignore`

Git ko batata hai kaun si cheezein GitHub par **nahi** bhejni:

- `__pycache__/` aur `*.pyc`: Python khud banata hai (compiled files), har computer par dobara ban jaati hain.
- `.venv/`: local installed packages ka folder, bohat bara hota hai, `requirements.txt` se dobara ban jaata hai.

## 8. `docs/`

Yeh do documents: files ka explanation (yeh file) aur `knapsack.py` ka line-by-line explanation.

---

## Poora flow, ek example ke saath

1. User "Lecture Example 2" chunta hai. `app.py` packages ko `st.session_state.pkgs` mein rakhta hai.
2. `app.py` lists banata hai: `profits = [10, 5, 15, 7, 6, 18, 3]`, `weights = [2, 3, 5, 7, 1, 4, 1]`, `capacity = 15`.
3. `app.py` → `compare_all(...)` (knapsack.py) → teeno answers: **47, 54, 55.33**, best = `max_ratio`.
4. `app.py` → `ui.stats(...)`, `ui.truck(...)`, `ui.comparison(...)` (ui.py) → HTML.
5. `st.html(...)` (streamlit) woh HTML browser mein dikhata hai.
6. User koi weight badle ya package tick kare to Streamlit poora `app.py` dobara chalata hai aur naya answer aa jaata hai.
