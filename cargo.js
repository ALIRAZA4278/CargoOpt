/*
  cargo.js - CargoOpt ka UI.
  Knapsack ka asli logic knapsack.js mein hai (dp01, greedy01).

  Mapping:
    truck capacity -> knapsack capacity
    package weight -> item weight
    package profit -> item value
*/

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const MAX_PACKAGES = 150, MAX_CAPACITY = 20000;
const STORE = "cargoopt.v1";

// ---------------- Sample scenarios ----------------
const PRESETS = {
  city: { label: "Sample: City delivery (100)", capacity: 100, items: [
    ["Medical supplies", 12, 340], ["Laptops", 25, 900], ["Office chairs", 40, 520], ["Groceries", 30, 260],
    ["Textiles", 18, 210], ["Electronics", 22, 640], ["Books", 28, 180], ["Spare parts", 15, 300]] },
  freight: { label: "Sample: Freight haul (500)", capacity: 500, items: [
    ["Machinery", 180, 2400], ["Furniture", 140, 1500], ["Appliances", 120, 1650], ["Auto parts", 90, 1300], ["Steel tools", 85, 1100],
    ["Paint drums", 75, 700], ["Packaged food", 110, 1050], ["Textile rolls", 60, 640], ["Electronics", 55, 1500],
    ["Toys", 45, 420], ["Stationery", 40, 380], ["Cosmetics", 30, 620]] },
  trap: { label: "Sample: Greedy trap (50)", capacity: 50, items: [
    ["Pallet A", 10, 60], ["Pallet B", 20, 100], ["Pallet C", 30, 110], ["Pallet D", 35, 130]] },
};

// ---------------- State ----------------
let packages = [];        // {id, name, weight, profit}
let loaded = new Set();   // loaded package ids
let nextId = 1;
let opt = null;           // DP / Greedy results (cache)
let animTimer = null, solveTimer = null;
let lastRendered = new Set();
let sort = { key: null, dir: 1 };
let currency = "$", unit = "kg";

const capacity = () => Math.min(MAX_CAPACITY, Math.max(1, parseInt($("cap").value) || 1));
// Har package ka fixed color (curated palette, taake sab harmonious dikhein)
const PALETTE = ["#0f766e", "#2563eb", "#7c3aed", "#db2777", "#ea580c", "#ca8a04", "#16a34a", "#0891b2", "#4f46e5", "#be123c", "#65a30d", "#9333ea"];
const color = id => PALETTE[(id - 1) % PALETTE.length];
const ICON = {
  box: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8l-9-5-9 5v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
  pie: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.2 15.9A10 10 0 1 1 8 2.8"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
  trend: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/></svg>',
};
const money = n => currency + (currency.length > 1 ? " " : "") + Math.round(n).toLocaleString("en-US");
const wt = n => `${n.toLocaleString("en-US")} ${unit}`;

// ---------------- Save / restore (browser storage) ----------------
function save() {
  try { localStorage.setItem(STORE, JSON.stringify({ packages, capacity: capacity(), currency, unit })); } catch (e) { /* ignore */ }
}
function restore() {
  try {
    const s = JSON.parse(localStorage.getItem(STORE));
    if (s && Array.isArray(s.packages)) return s;
  } catch (e) { /* ignore */ }
  return null;
}
function markCustom() { $("preset").value = "custom"; }

// ---------------- Algorithms (knapsack.js) ----------------
function solveAll() {
  const w = packages.map(p => p.weight), v = packages.map(p => p.profit), cap = capacity();
  const t0 = performance.now();
  const dp = dp01(w, v, cap);
  const ms = performance.now() - t0;
  const greedyRatio = greedy01(w, v, cap);

  // Greedy #2: sabse zyada profit wala pehle (ratio ignore)
  const order = packages.map((_, i) => i).sort((a, b) => v[b] - v[a]);
  let tw = 0, tv = 0; const ch = [];
  for (const i of order) if (tw + w[i] <= cap) { ch.push(i); tw += w[i]; tv += v[i]; }

  opt = { dp, ms, greedyRatio, greedyProfit: { best: tv, chosen: ch }, cells: (packages.length + 1) * (cap + 1) };
}

const idsOf = idxs => idxs.map(i => packages[i].id);
const pick = ids => packages.filter(p => ids.includes(p.id));
const wOf = ids => pick(ids).reduce((s, p) => s + p.weight, 0);
const vOf = ids => pick(ids).reduce((s, p) => s + p.profit, 0);

// ---------------- Rendering ----------------
function refresh() { solveAll(); render(); save(); }

function render() {
  const cap = capacity();
  const ids = [...loaded];
  const lw = wOf(ids), lp = vOf(ids);
  const util = lw / cap * 100;
  const optProfit = opt.dp.best;
  const eff = optProfit ? lp / optProfit * 100 : 100;
  const has = packages.length > 0;

  // KPI cards
  const effCls = lp === 0 ? "" : eff >= 100 ? "good" : eff >= 80 ? "warn" : "bad";
  const profitPct = optProfit ? Math.min(100, lp / optProfit * 100) : 0;
  $("kpis").innerHTML = `
    <div class="kpi"><div class="ico">${esc(currency)}</div><div><span>Profit loaded</span><b>${money(lp)}</b><small>of ${money(optProfit)} possible</small>
      <div class="mini"><i style="width:${profitPct}%"></i></div></div></div>
    <div class="kpi"><div class="ico">${ICON.box}</div><div><span>Weight loaded</span><b>${wt(lw)}</b><small>${wt(cap - lw)} free</small>
      <div class="mini"><i style="width:${Math.min(100, util)}%"></i></div></div></div>
    <div class="kpi"><div class="ico">${ICON.pie}</div><div><span>Utilization</span><b>${util.toFixed(0)}%</b><small>${ids.length} of ${packages.length} packages</small>
      <div class="mini"><i style="width:${Math.min(100, util)}%"></i></div></div></div>
    <div class="kpi ${effCls}"><div class="ico">${ICON.trend}</div><div><span>Efficiency</span><b>${lp === 0 ? "-" : eff.toFixed(0) + "%"}</b><small>vs optimal plan</small>
      <div class="mini"><i style="width:${Math.min(100, eff)}%"></i></div></div></div>`;

  // Cargo bay (segment width = weight / capacity)
  $("load").innerHTML = packages.filter(p => loaded.has(p.id)).map(p => {
    const pct = p.weight / cap * 100;
    const label = pct >= 9 ? `${esc(p.name)}<small>${p.weight} ${unit}</small>` : "";
    return `<div class="seg ${lastRendered.has(p.id) ? "" : "new"}" style="flex:0 0 ${pct}%;background:${color(p.id)}" title="${esc(p.name)}: ${wt(p.weight)}, ${money(p.profit)}">${label}</div>`;
  }).join("");
  lastRendered = new Set(loaded);
  $("bayInfo").textContent = `${lw} / ${cap} ${unit}`;
  $("capMin").textContent = `0 ${unit}`;
  $("capMid").textContent = `${Math.round(cap / 2)} ${unit}`;
  $("capMax").textContent = `${cap} ${unit}`;
  $("meter").style.width = Math.min(100, util) + "%";
  $("opt").disabled = !has;
  $("clear").disabled = !loaded.size;
  $("csv").disabled = !loaded.size;
  $("wipe").disabled = !has;

  renderManifest(lw, lp, cap);
  renderStrategies(lp, lw, cap);
  renderDpTable(cap);
  $("printMeta").textContent = `Generated ${new Date().toLocaleString()} - Truck capacity ${cap} ${unit}`;
}

function sortedPackages() {
  if (!sort.key) return packages;
  const val = p => sort.key === "ratio" ? p.profit / p.weight : sort.key === "name" ? p.name.toLowerCase() : p[sort.key];
  return [...packages].sort((a, b) => (val(a) > val(b) ? 1 : val(a) < val(b) ? -1 : 0) * sort.dir);
}

function renderManifest(lw, lp, cap) {
  for (const k of ["name", "weight", "profit", "ratio"]) $("s-" + k).textContent = sort.key === k ? (sort.dir > 0 ? "▲" : "▼") : "";

  if (!packages.length) {
    $("rows").innerHTML = `<tr><td colspan="6"><div class="empty"><b>No packages yet</b>
      Add packages on the left, paste a list, upload a CSV, or pick a sample from "Data source".</div></td></tr>`;
    $("foot").innerHTML = "";
    return;
  }
  $("rows").innerHTML = sortedPackages().map(p => {
    const heavy = p.weight > cap, on = loaded.has(p.id);
    return `<tr class="${on ? "on" : ""} ${heavy ? "heavy" : ""}">
      <td class="no-print"><input type="checkbox" data-id="${p.id}" ${on ? "checked" : ""} ${heavy ? "disabled" : ""} aria-label="Load ${esc(p.name)}"></td>
      <td><div class="namecell"><span class="dot" style="background:${color(p.id)}"></span>
        <input class="cell" data-f="name" data-id="${p.id}" value="${esc(p.name)}" maxlength="40" aria-label="Name">
        ${heavy ? '<span class="badge" title="Heavier than the truck capacity">too heavy</span>' : ""}</div></td>
      <td class="r"><input class="cell num" type="number" min="1" step="1" data-f="weight" data-id="${p.id}" value="${p.weight}" aria-label="Weight"></td>
      <td class="r"><input class="cell num" type="number" min="0" step="1" data-f="profit" data-id="${p.id}" value="${p.profit}" aria-label="Profit"></td>
      <td class="r" style="padding-right:14px">${(p.profit / p.weight).toFixed(1)}</td>
      <td class="no-print"><button class="del" data-del="${p.id}" title="Remove" aria-label="Remove ${esc(p.name)}">&times;</button></td>
    </tr>`;
  }).join("");

  const left = packages.filter(p => !loaded.has(p.id));
  $("foot").innerHTML = `
    <tr><td class="no-print"></td><td>Loaded total (${loaded.size})</td><td class="r">${wt(lw)}</td><td class="r">${money(lp)}</td><td></td><td class="no-print"></td></tr>
    <tr class="sub"><td class="no-print"></td><td>Left behind (${left.length})</td><td class="r">${wt(left.reduce((s, p) => s + p.weight, 0))}</td>
      <td class="r">${money(left.reduce((s, p) => s + p.profit, 0))}</td><td></td><td class="no-print"></td></tr>`;
}

function renderStrategies(lp, lw, cap) {
  if (!packages.length) {
    $("strats").innerHTML = `<p class="hint">Add packages to compare strategies.</p>`;
    $("insight").textContent = ""; $("algo").textContent = "";
    return;
  }
  const rows = [
    { name: "Your load", sub: "Manual selection", profit: lp, weight: lw, show: lw > 0 },
    { name: "Greedy: highest profit", sub: "Biggest profit first", profit: opt.greedyProfit.best, weight: wOf(idsOf(opt.greedyProfit.chosen)) },
    { name: "Greedy: best ratio", sub: "Highest profit per weight first", profit: opt.greedyRatio.best, weight: wOf(idsOf(opt.greedyRatio.chosen)) },
    { name: "Dynamic Programming", sub: "Optimal, always", profit: opt.dp.best, weight: wOf(idsOf(opt.dp.chosen)), best: true },
  ].filter(r => r.show !== false);

  const max = Math.max(1, opt.dp.best);
  $("strats").innerHTML = rows.map(r => `
    <div class="strat ${r.best ? "best" : ""}">
      <div><b>${r.name}${r.best ? '<span class="tag">Optimal</span>' : ""}</b><small>${r.sub}</small></div>
      <div class="bar"><i style="width:${r.profit / max * 100}%"></i></div>
      <div class="num">${money(r.profit)}<small>${(r.weight / cap * 100).toFixed(0)}% full</small></div>
    </div>`).join("");

  const d = opt.dp.best, bestGreedy = Math.max(opt.greedyRatio.best, opt.greedyProfit.best);
  let msg;
  if (d === 0) msg = "No package fits in this truck. Increase the capacity or reduce package weights.";
  else if (bestGreedy < d) msg = `Greedy leaves ${money(d - bestGreedy)} on the table (${((d - bestGreedy) / d * 100).toFixed(1)}%). DP finds the true best combination.`;
  else msg = "On this shipment Greedy happens to match DP. That is not guaranteed for 0/1 Knapsack: try the Greedy trap sample.";
  $("insight").textContent = msg;
  $("algo").textContent = `DP table: ${packages.length + 1} x ${cap + 1} = ${opt.cells.toLocaleString()} cells, solved in ${opt.ms < 0.1 ? "<0.1" : opt.ms.toFixed(1)} ms. Time complexity O(n x W).`;
}

function renderDpTable(cap) {
  const n = packages.length;
  if (!n) { $("dpNote").textContent = "Add packages to see the table."; $("dpTable").innerHTML = ""; return; }
  if (n > 15 || cap > 60) {
    $("dpNote").textContent = `The table has ${(n + 1)} x ${(cap + 1)} cells, too large to display. Use n ≤ 15 packages and capacity ≤ 60 to inspect it.`;
    $("dpTable").innerHTML = ""; return;
  }
  $("dpNote").textContent = "Cell (row i, column w) = best profit using the first i packages with w capacity. Highlighted cells are where a package was chosen (backtracking).";
  const hit = new Set(opt.dp.path.map(([i, w]) => i + "," + w));
  let h = `<table class="dp"><tr><th>Package \\ ${unit}</th>`;
  for (let w = 0; w <= cap; w++) h += `<th>${w}</th>`;
  h += "</tr>";
  for (let i = 0; i <= n; i++) {
    h += `<tr><th>${i === 0 ? "(none)" : esc(packages[i - 1].name)}</th>`;
    for (let w = 0; w <= cap; w++) h += `<td${hit.has(i + "," + w) ? ' class="pick"' : ""}>${opt.dp.table[i][w]}</td>`;
    h += "</tr>";
  }
  $("dpTable").innerHTML = h + "</table>";
}

// ---------------- Actions ----------------
function toast(msg) {
  const t = $("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove("show"), 2600);
}

function stopAnim() { clearTimeout(animTimer); }

function togglePackage(id, on) {
  const p = packages.find(x => x.id === id);
  if (on) {
    const free = capacity() - wOf([...loaded]);
    if (p.weight > free) { toast(`"${p.name}" doesn't fit: only ${free} ${unit} free`); return render(); }
    loaded.add(id);
  } else loaded.delete(id);
  render();
}

// DP ka answer ek ek package kar ke truck mein load karna (animation)
function optimize() {
  stopAnim();
  const order = idsOf(opt.dp.chosen);
  loaded = new Set(); lastRendered = new Set(); render();
  if (!order.length) return toast("Nothing fits in this truck");
  let k = 0;
  (function step() {
    loaded.add(order[k++]); render();
    if (k < order.length) animTimer = setTimeout(step, 260);
    else toast(`Optimal load: ${money(opt.dp.best)} profit`);
  })();
}

function addPackage(name, weight, profit) {
  packages.push({ id: nextId++, name, weight, profit });
}

// "name, weight, profit" lines -> rows
function parseRows(text) {
  const rows = []; let skipped = 0, first = true;
  const num = s => Number(String(s).replace(/[^0-9.\-]/g, ""));
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const parts = line.split(/[,;\t]/).map(s => s.trim().replace(/^"|"$/g, ""));
    const isHeader = first && parts.length >= 3 && !/\d/.test(parts[parts.length - 2]); // pehli line header ho sakti hai (weight mein koi digit nahi)
    first = false;
    if (isHeader) continue;
    if (parts.length < 3) { skipped++; continue; }
    const profit = num(parts.pop()), weight = num(parts.pop()), name = parts.join(", ").slice(0, 40);
    if (!name || !(weight >= 1) || !(profit >= 0) || !isFinite(weight) || !isFinite(profit)) { skipped++; continue; }
    rows.push({ name, weight: Math.round(weight), profit: Math.round(profit) });
  }
  return { rows, skipped };
}

function importText(text, replace) {
  const { rows, skipped } = parseRows(text);
  if (!rows.length) { $("bulkMsg").textContent = "No valid rows found. Use: name, weight, profit"; return false; }
  const base = replace ? [] : packages;
  if (base.length + rows.length > MAX_PACKAGES) { $("bulkMsg").textContent = `Too many packages (limit ${MAX_PACKAGES}).`; return false; }
  stopAnim();
  if (replace) { packages = []; loaded = new Set(); }
  rows.forEach(r => addPackage(r.name, r.weight, r.profit));
  $("bulkMsg").textContent = "";
  markCustom(); refresh();
  toast(`${replace ? "Replaced with" : "Added"} ${rows.length} package${rows.length > 1 ? "s" : ""}${skipped ? ` (${skipped} row${skipped > 1 ? "s" : ""} skipped)` : ""}`);
  return true;
}

function download(name, text, type) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name; a.click(); URL.revokeObjectURL(a.href);
}

function exportCsv() {
  const rows = packages.filter(p => loaded.has(p.id));
  if (!rows.length) return toast("Load some packages first");
  const ids = rows.map(p => p.id);
  const csv = [`Package,Weight (${unit}),Profit (${currency})`, ...rows.map(p => `"${p.name.replace(/"/g, '""')}",${p.weight},${p.profit}`),
    `TOTAL,${wOf(ids)},${vOf(ids)}`].join("\n");
  download("cargo-manifest.csv", csv, "text/csv");
}

// ---------------- Events ----------------
$("preset").innerHTML = `<option value="custom">My data</option><option value="blank">Start blank</option>` +
  Object.entries(PRESETS).map(([k, p]) => `<option value="${k}">${p.label}</option>`).join("");

$("preset").onchange = e => {
  stopAnim(); loaded = new Set(); lastRendered = new Set();
  const k = e.target.value;
  if (k === "blank") { packages = []; }
  else if (PRESETS[k]) {
    $("cap").value = PRESETS[k].capacity;
    packages = PRESETS[k].items.map(([name, weight, profit]) => ({ id: nextId++, name, weight, profit }));
  }
  refresh();
  if (k === "blank") $("n").focus();
};

$("cap").oninput = () => {
  stopAnim(); clearTimeout(solveTimer);
  markCustom();
  solveTimer = setTimeout(() => {
    if (wOf([...loaded]) > capacity()) { loaded = new Set(); toast("Capacity reduced, truck unloaded"); }
    refresh();
  }, 250);
};
$("unit").onchange = e => { unit = e.target.value; refresh(); };
$("cur").onchange = e => { currency = e.target.value; refresh(); };

$("opt").onclick = optimize;
$("clear").onclick = () => { stopAnim(); loaded = new Set(); render(); };
$("csv").onclick = exportCsv;
$("print").onclick = () => window.print();
$("wipe").onclick = () => {
  if (!confirm(`Delete all ${packages.length} packages?`)) return;
  stopAnim(); packages = []; loaded = new Set(); markCustom(); refresh();
};

// Table: checkbox, delete, inline edit, sort
$("rows").onclick = e => {
  const cb = e.target.closest("input[data-id][type=checkbox]"), del = e.target.closest("[data-del]");
  if (cb) togglePackage(+cb.dataset.id, cb.checked);
  if (del) { const id = +del.dataset.del; packages = packages.filter(p => p.id !== id); loaded.delete(id); markCustom(); refresh(); }
};
$("rows").onchange = e => {
  const inp = e.target.closest("input.cell");
  if (!inp) return;
  const p = packages.find(x => x.id === +inp.dataset.id), f = inp.dataset.f;
  if (f === "name") {
    const v = inp.value.trim();
    if (!v) { toast("Name cannot be empty"); return render(); }
    p.name = v;
  } else {
    const v = Number(inp.value);
    if (!Number.isInteger(v) || v < (f === "weight" ? 1 : 0)) { toast(f === "weight" ? "Weight must be a whole number ≥ 1" : "Profit must be a whole number ≥ 0"); return render(); }
    p[f] = v;
  }
  if (loaded.has(p.id) && wOf([...loaded]) > capacity()) { loaded.delete(p.id); toast(`"${p.name}" no longer fits, unloaded`); }
  markCustom(); refresh();
};
document.querySelector("thead").onclick = e => {
  const th = e.target.closest("th.sort");
  if (!th) return;
  sort = sort.key === th.dataset.k ? { key: th.dataset.k, dir: -sort.dir } : { key: th.dataset.k, dir: 1 };
  render();
};

// Add form
$("addForm").onsubmit = e => {
  e.preventDefault();
  const name = $("n").value.trim(), weight = Number($("w").value), profit = Number($("p").value);
  const err = !name ? "Enter a package name." : !Number.isInteger(weight) || weight < 1 ? "Weight must be a whole number of at least 1."
    : !Number.isInteger(profit) || profit < 0 ? "Profit must be a whole number, 0 or more."
    : packages.length >= MAX_PACKAGES ? `Limit of ${MAX_PACKAGES} packages reached.` : "";
  $("formErr").textContent = err;
  if (err) return;
  addPackage(name, weight, profit);
  e.target.reset(); $("n").focus(); markCustom(); refresh();
};

// Bulk import
$("bulkAdd").onclick = () => { if (importText($("bulk").value, false)) $("bulk").value = ""; };
$("bulkReplace").onclick = () => { if (importText($("bulk").value, true)) $("bulk").value = ""; };
$("file").onchange = e => {
  const f = e.target.files[0];
  if (!f) return;
  if (f.size > 1024 * 1024) { $("bulkMsg").textContent = "File too large (max 1 MB)."; return; }
  const r = new FileReader();
  r.onload = () => importText(String(r.result), false);
  r.readAsText(f);
  e.target.value = "";
};
$("tpl").onclick = () => download("cargo-template.csv", "Package,Weight,Profit\nLaptops,25,900\nOffice chairs,40,520\nMedical supplies,12,340\n", "text/csv");

// ---------------- Start ----------------
(function init() {
  const s = restore();
  if (s && s.packages.length) {
    currency = ["$", "Rs", "€", "£"].includes(s.currency) ? s.currency : "$";
    unit = ["kg", "lb", "ton"].includes(s.unit) ? s.unit : "kg";
    $("cur").value = currency; $("unit").value = unit;
    $("cap").value = Math.min(MAX_CAPACITY, Math.max(1, parseInt(s.capacity) || 100));
    packages = s.packages
      .filter(p => p && typeof p.name === "string" && p.weight >= 1 && p.profit >= 0)
      .slice(0, MAX_PACKAGES).map(p => ({ id: nextId++, name: p.name.slice(0, 40), weight: Math.round(p.weight), profit: Math.round(p.profit) }));
    $("preset").value = "custom";
  } else {
    $("preset").value = "city";
    $("cap").value = PRESETS.city.capacity;
    packages = PRESETS.city.items.map(([name, weight, profit]) => ({ id: nextId++, name, weight, profit }));
  }
  refresh();
})();
