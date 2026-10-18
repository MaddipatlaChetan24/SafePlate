/* SafePlate web client — vanilla JS, no build step. */

const ICONS = {
  sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
  calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  book: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
  box: '<path d="M21 8 12 3 3 8v8l9 5 9-5Z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  gauge: '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
  heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  cart: '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
  star: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="currentColor"/>',
  trash: '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  bulb: '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5M9 18h6M10 22h4"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8M21 3v5h-5M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16M8 16H3v5"/>',
  loader: '<path d="M21 12a9 9 0 1 1-6.22-8.56"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  chart: '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
};
const icon = (name, cls = "i") =>
  `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ""}</svg>`;

const ALLERGIES = ["nuts", "peanut", "dairy", "gluten", "egg", "shellfish", "fish", "soy", "sesame"];
const QUICK = ["chicken", "garlic", "lemon", "tofu", "broccoli", "pasta", "tomatoes", "eggs", "spinach", "chickpeas", "salmon", "rice"];
const STAPLES = ["rice", "pasta", "onion", "garlic", "olive oil", "soy sauce", "eggs", "canned tomatoes", "chickpeas", "lentils", "butter", "flour"];

const VISUALS = [
  [/pasta|spaghetti|pomodoro|penne/i, "🍝", ["#fde68a", "#fca5a5"]],
  [/taco|burrito/i, "🌮", ["#fde68a", "#86efac"]],
  [/curry|masala|dal/i, "🍛", ["#fed7aa", "#fcd34d"]],
  [/soup|stew|broth/i, "🍲", ["#fecaca", "#fed7aa"]],
  [/salmon|fish|cod|tuna/i, "🐟", ["#bae6fd", "#c7d2fe"]],
  [/frittata|omelet|shakshuka|egg/i, "🍳", ["#fef08a", "#fed7aa"]],
  [/noodle|ramen|pad/i, "🍜", ["#fde68a", "#fbcfe8"]],
  [/salad|bowl/i, "🥗", ["#bbf7d0", "#d9f99d"]],
  [/stir-fry|tofu|broccoli/i, "🥦", ["#bbf7d0", "#a7f3d0"]],
  [/chicken/i, "🍗", ["#fed7aa", "#fde68a"]],
  [/pizza/i, "🍕", ["#fecaca", "#fde68a"]],
];
const visual = (r) => {
  for (const [re, emoji, g] of VISUALS) if (re.test(r.name)) return { emoji, g };
  return { emoji: "🍽️", g: ["#e9d5ff", "#fbcfe8"] };
};
const heroStyle = (v) => `background: linear-gradient(135deg, ${v.g[0]}, ${v.g[1]})`;

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const $ = (sel) => document.querySelector(sel);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const state = {
  ingredients: [],
  allergies: [],
  servings: 2,
  count: 3,
  pantry: [],
  saved: new Map(), // recipe name -> cookbook id
  last: null,
  lastPrefs: null,
  plan: null,
  planDays: 5,
  drawer: null,
};

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return (res.headers.get("content-type") || "").includes("json") ? res.json() : res.text();
}

function toast(msg) {
  const el = document.createElement("div");
  el.className = "toast";
  el.innerHTML = `${icon("check")}<span>${esc(msg)}</span>`;
  $("#toasts").appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    el.outerHTML = icon(el.dataset.icon, ["i", ...el.classList].join(" "));
  });
}

function download(name, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/* ---------- Navigation & theme ---------- */

const PAGES = {
  discover: ["Discover", "Turn what's in your kitchen into dinner, checked against your allergies and diet."],
  planner: ["Meal Planner", "A varied week of dinners that shares ingredients, with one shopping list."],
  cookbook: ["Cookbook", "Recipes you've saved and rated. High ratings shape future suggestions."],
  pantry: ["Pantry", "Ingredients you always have. Include them in any search with one click."],
  history: ["History", "Recent searches. Run any of them again."],
};

function go(view) {
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${view}`));
  $("#page-title").textContent = PAGES[view][0];
  $("#page-sub").textContent = PAGES[view][1];
  $("#sidebar").classList.remove("open");
  if (view === "cookbook") loadCookbook();
  if (view === "history") loadHistory();
  if (view === "pantry") renderPantry();
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem("sp-theme", theme); } catch {}
}
function initTheme() {
  let theme = null;
  try { theme = localStorage.getItem("sp-theme"); } catch {}
  const params = new URLSearchParams(location.search);
  theme = params.get("theme") || theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.dataset.theme = theme;
}

/* ---------- Discover: inputs ---------- */

function renderIngredients() {
  $("#ingredient-chips").innerHTML = state.ingredients
    .map((i, k) => `<span class="chip">${esc(i)}<button data-rm="${k}" aria-label="Remove ${esc(i)}">${icon("x")}</button></span>`)
    .join("");
  $("#quick-adds").innerHTML = QUICK.filter((q) => !state.ingredients.includes(q))
    .slice(0, 6)
    .map((q) => `<button class="quick" data-add="${esc(q)}">+ ${esc(q)}</button>`)
    .join("");
}

function addIngredients(text) {
  text.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean).forEach((i) => {
    if (!state.ingredients.includes(i)) state.ingredients.push(i);
  });
  renderIngredients();
}

function renderAllergies() {
  $("#f-allergies").innerHTML = ALLERGIES.map(
    (a) => `<button class="toggle-chip ${state.allergies.includes(a) ? "on" : ""}" data-allergy="${a}">${state.allergies.includes(a) ? icon("x") : ""}${cap(a)}</button>`
  ).join("");
  $("#f-allergies").querySelectorAll("svg.i").forEach((s) => { s.style.width = "12px"; s.style.height = "12px"; });
}

function prefs() {
  return {
    diet: $("#f-diet").value,
    allergies: [...state.allergies],
    cuisine: $("#f-cuisine").value.trim(),
    max_minutes: Number($("#f-time").value),
    servings: state.servings,
  };
}

/* ---------- Agent trace ---------- */

function renderTrace(steps) {
  const el = $("#trace");
  el.hidden = false;
  el.innerHTML = steps
    .map((s, k) => {
      const ico = s.state === "run" ? "loader" : s.state === "fixed" ? "wrench" : s.state === "done" ? "check" : s.icon;
      const line = k < steps.length - 1 ? `<div class="trace-line ${s.state === "done" || s.state === "fixed" ? "done" : ""}"></div>` : "";
      return `<div class="trace-step ${s.state}"><div class="trace-ico">${icon(ico)}</div><div><div class="trace-title">${esc(s.title)}</div><div class="trace-sub">${esc(s.sub)}</div></div></div>${line}`;
    })
    .join("");
}

function constraintSummary(p) {
  const parts = [];
  if (p.diet) parts.push(cap(p.diet));
  p.allergies.forEach((a) => parts.push(`${cap(a === "nuts" ? "nut" : a)}-free`));
  if (p.max_minutes) parts.push(`≤ ${p.max_minutes} min`);
  return parts;
}

/* ---------- Discover: generate ---------- */

async function generate() {
  const pending = $("#ingredient-input").value.trim();
  if (pending) { addIngredients(pending); $("#ingredient-input").value = ""; }
  const p = prefs();
  const usePantry = $("#use-pantry").checked;
  const total = state.ingredients.length + (usePantry ? state.pantry.filter((x) => !state.ingredients.includes(x)).length : 0);
  const constraints = constraintSummary(p);

  $("#discover-empty").hidden = true;
  $("#results-layout").hidden = false;
  $("#results").innerHTML = Array.from({ length: state.count }, () => skeletonCard()).join("");
  $("#shopping-card").innerHTML = `<div class="sk" style="width:60%;margin-bottom:16px"></div>${'<div class="sk" style="margin:12px 0"></div>'.repeat(5)}`;
  renderTrace([
    { state: "done", title: "Read your kitchen", sub: `${total} ingredient${total === 1 ? "" : "s"}${usePantry ? " incl. pantry" : ""}`, icon: "list" },
    { state: "run", title: "Generating recipes", sub: "Chef + nutritionist prompt", icon: "sparkles" },
    { state: "idle", title: "Safety check", sub: constraints.length ? constraints.join(" · ") : "No hard constraints", icon: "shield" },
    { state: "idle", title: "Verified", sub: "Ready to cook", icon: "check" },
  ]);
  const btn = $("#generate-btn");
  btn.disabled = true;
  btn.innerHTML = `${icon("loader")}Generating…`;
  btn.querySelector("svg").style.animation = "spin 1s linear infinite";

  try {
    const [data] = await Promise.all([
      api("/api/suggest", { method: "POST", body: { ingredients: state.ingredients, use_pantry: usePantry, preferences: p, count: state.count } }),
      new Promise((r) => setTimeout(r, 650)), // let the trace animation read
    ]);
    state.last = data;
    state.lastPrefs = p;
    const fixes = data.trace.corrections.length;
    renderTrace([
      { state: "done", title: "Read your kitchen", sub: `${data.ingredients.length} ingredients${usePantry ? " incl. pantry" : ""}`, icon: "list" },
      { state: "done", title: `Generated ${data.recipes.length} recipe${data.recipes.length === 1 ? "" : "s"}`, sub: `${data.trace.attempts} attempt${data.trace.attempts === 1 ? "" : "s"}`, icon: "sparkles" },
      fixes
        ? { state: "fixed", title: `Self-corrected ${fixes} issue${fixes === 1 ? "" : "s"}`, sub: data.trace.corrections[0], icon: "shield" }
        : { state: "done", title: "Safety check passed", sub: constraints.length ? constraints.join(" · ") : "No hard constraints", icon: "shield" },
      { state: "done", title: "Verified", sub: `${data.recipes.length} safe to cook`, icon: "check" },
    ]);
    renderResults();
  } catch (e) {
    $("#results").innerHTML = `<div class="card">Something went wrong: ${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${icon("sparkles")}Generate recipes`;
  }
}

function skeletonCard() {
  return `<div class="rcard skeleton"><div class="rcard-hero"></div><div class="rcard-body">
    <div class="sk" style="width:35%"></div><div class="sk" style="width:85%;height:16px"></div>
    <div class="sk" style="width:65%"></div><div class="sk" style="height:6px"></div></div></div>`;
}

function recipeCard(r, { recommended = false, prefsUsed = null, footer = "", idx = 0, attr = "" } = {}) {
  const v = visual(r);
  const n = r.nutrition_per_serving;
  const used = (r.uses || []).length;
  const pct = Math.round((used / Math.max(r.ingredients.length, 1)) * 100);
  const tags = prefsUsed ? constraintSummary(prefsUsed).map((t) => `<span class="badge ok">${icon("check")}${esc(t)}</span>`) : [];
  if (r.missing_ingredients.length) tags.push(`<span class="badge warn">${icon("cart")}Buy ${r.missing_ingredients.length}</span>`);
  else tags.push(`<span class="badge ok">${icon("check")}Nothing to buy</span>`);
  const saved = state.saved.has(r.name);
  return `
    <article class="rcard" ${attr} style="animation-delay:${idx * 70}ms">
      <div class="rcard-hero" style="${heroStyle(v)}">
        ${recommended ? `<span class="badge">${icon("sparkles")}Best match</span>` : ""}
        <button class="fav ${saved ? "on" : ""}" data-fav aria-label="Save">${icon("heart")}</button>
        <span class="emoji">${v.emoji}</span>
      </div>
      <div class="rcard-body">
        <div>
          <div class="rcard-cuisine">${esc(r.cuisine)}</div>
          <div class="rcard-title">${esc(r.name)}</div>
        </div>
        <div class="meta">
          <span>${icon("clock")}${r.total_minutes} min</span>
          <span>${icon("flame")}${n.calories} kcal</span>
          <span>${icon("gauge")}${esc(r.difficulty)}</span>
        </div>
        <div class="usage">
          <div class="usage-top"><span><b>${used}</b> of ${r.ingredients.length} ingredients on hand</span><span>${pct}%</span></div>
          <div class="bar"><i style="width:${pct}%"></i></div>
        </div>
        <div class="tags">${tags.join("")}</div>
      </div>
      ${footer}
    </article>`;
}

function renderResults() {
  const d = state.last;
  if (!d.recipes.length) {
    $("#results").innerHTML = `<div class="card">No recipe could satisfy every constraint. Try relaxing the time limit or adding ingredients.</div>`;
  } else {
    $("#results").innerHTML = d.recipes
      .map((r, k) => recipeCard(r, { recommended: r.name === d.recommended, prefsUsed: state.lastPrefs, idx: k, attr: `data-idx="${k}"` }))
      .join("");
  }
  $("#shopping-card").innerHTML = shoppingCard(d.shopping_list, "Shopping list", `${d.recipes.length} recipes`);
}

function shoppingCard(items, title, sub) {
  const body = items.length
    ? `<ul class="shop-list">${items.map((i) => `<li><input type="checkbox" /><span>${esc(i.label)}</span></li>`).join("")}</ul>
       <div class="side-actions"><button class="btn sm" data-copy-list>${icon("copy")}Copy</button></div>`
    : `<div class="pill-ok">${icon("check")}You have everything</div>`;
  return `<div class="card-head"><h3>${icon("cart")} ${esc(title)}</h3><span class="muted small">${esc(sub)}</span></div>${body}`;
}

/* ---------- Drawer ---------- */

function openDrawer(recipe, ctx = {}) {
  state.drawer = { recipe, ctx, base: ctx.base || recipe };
  renderDrawer();
  $("#drawer").classList.add("open");
  $("#drawer-backdrop").classList.add("open");
  $("#drawer").setAttribute("aria-hidden", "false");
  $("#drawer").scrollTop = 0;
}
function closeDrawer() {
  $("#drawer").classList.remove("open");
  $("#drawer-backdrop").classList.remove("open");
  $("#drawer").setAttribute("aria-hidden", "true");
}

function renderDrawer() {
  const { recipe: r } = state.drawer;
  const v = visual(r);
  const n = r.nutrition_per_serving;
  const kc = { p: n.protein_g * 4, c: n.carbs_g * 4, f: n.fat_g * 9 };
  const tot = kc.p + kc.c + kc.f || 1;
  const a1 = (kc.p / tot) * 360, a2 = a1 + (kc.c / tot) * 360;
  const donut = `conic-gradient(var(--protein) 0 ${a1}deg, var(--carbs) ${a1}deg ${a2}deg, var(--fat) ${a2}deg 360deg)`;
  const missing = new Set(r.missing_ingredients.map((i) => i.name));
  const uses = new Set(r.uses || []);
  const ingRow = (i) => {
    const kind = uses.has(i.name) ? "have" : missing.has(i.name) ? "buy" : "base";
    const ico = kind === "have" ? "check" : kind === "buy" ? "plus" : "box";
    return `<li><span class="ing-dot ${kind}">${icon(ico)}</span><span>${esc(label(i))}</span></li>`;
  };
  const maxMacro = Math.max(n.protein_g, n.carbs_g, n.fat_g, 1);
  const macro = (name, val, color) =>
    `<div class="macro" style="--c:${color}"><span>${name}</span><div class="bar"><i style="width:${(val / maxMacro) * 100}%"></i></div><b>${val}g</b></div>`;
  const saved = state.saved.has(r.name);

  $("#drawer").innerHTML = `
    <div class="d-hero" style="${heroStyle(v)}">
      <button class="icon-btn d-close" data-close aria-label="Close">${icon("x")}</button>
      <span class="emoji">${v.emoji}</span>
    </div>
    <div class="d-body">
      <div class="d-title">
        <div class="rcard-cuisine">${esc(r.cuisine)} · ${esc(r.difficulty)}</div>
        <h2>${esc(r.name)}</h2>
        <div class="meta">
          <span>${icon("clock")}Prep ${r.prep_minutes} min</span>
          <span>${icon("flame")}Cook ${r.cook_minutes} min</span>
          <span>${icon("users")}Serves ${r.servings}</span>
        </div>
      </div>
      <div class="d-bar">
        <div style="display:flex;align-items:center;gap:10px"><span class="field-label">Servings</span>
          <div class="stepper"><button data-serv="-1">−</button><span>${r.servings}</span><button data-serv="1">+</button></div>
        </div>
        <div class="d-actions">
          <button class="btn ${saved ? "" : "primary"}" data-save>${icon("heart")}${saved ? "Saved" : "Save"}</button>
          <button class="btn" data-export>${icon("download")}Markdown</button>
        </div>
      </div>
      <div class="d-cols">
        <div class="d-section">
          <h3>Ingredients</h3>
          <ul class="ing-list">${r.ingredients.map(ingRow).join("")}</ul>
          <div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap" class="small muted">
            <span><span class="ing-dot have" style="display:inline-grid;vertical-align:middle">${icon("check")}</span> on hand</span>
            <span><span class="ing-dot buy" style="display:inline-grid;vertical-align:middle">${icon("plus")}</span> to buy</span>
          </div>
        </div>
        <div class="d-section">
          <h3>Method</h3>
          <ol class="steps">${r.instructions.map((s) => `<li><span>${esc(s.replace(/^step\s*\d+[:.]\s*/i, ""))}</span></li>`).join("")}</ol>
        </div>
      </div>
      <div class="d-section">
        <h3>Nutrition per serving</h3>
        <div class="nutri">
          <div class="donut" style="background:${donut}"><div class="donut-inner"><div><b>${n.calories}</b><br><span>kcal</span></div></div></div>
          <div class="macros">${macro("Protein", n.protein_g, "var(--protein)")}${macro("Carbs", n.carbs_g, "var(--carbs)")}${macro("Fat", n.fat_g, "var(--fat)")}</div>
        </div>
      </div>
      ${r.substitutions.length ? `<div class="d-section"><h3>Smart swaps</h3><div class="swaps">${r.substitutions.map((s) => `<span class="swap">${esc(s.replace("->", "→"))}</span>`).join("")}</div></div>` : ""}
      ${r.tips ? `<div class="callout">${icon("bulb")}<div><b>Chef's tip.</b> ${esc(r.tips)}</div></div>` : ""}
    </div>`;
}

function label(i) {
  if (i.quantity == null) return `${i.name} (to taste)`;
  const q = Number.isInteger(i.quantity) ? i.quantity : +i.quantity.toFixed(2);
  return `${q} ${i.unit || ""} ${i.name}`.replace(/\s+/g, " ").trim();
}

async function scaleDrawer(delta) {
  const { base, recipe } = state.drawer;
  const servings = Math.max(1, Math.min(20, recipe.servings + delta));
  if (servings === recipe.servings) return;
  const scaled = await api("/api/scale", { method: "POST", body: { recipe: base, servings } });
  scaled.uses = recipe.uses;
  state.drawer.recipe = scaled;
  renderDrawer();
}

async function saveRecipe(r) {
  if (state.saved.has(r.name)) return toast("Already in your cookbook");
  const { id } = await api("/api/cookbook", { method: "POST", body: r });
  state.saved.set(r.name, id);
  updateCounts();
  toast(`Saved “${r.name}”`);
}

async function exportRecipe(r) {
  const md = await api("/api/export/markdown", { method: "POST", body: r });
  download(`${slug(r.name)}.md`, md);
}

/* ---------- Planner ---------- */

async function makePlan() {
  const p = prefs();
  const ingredients = $("#plan-ingredients").value.split(",").map((s) => s.trim()).filter(Boolean);
  const btn = $("#plan-btn");
  btn.disabled = true;
  btn.innerHTML = `${icon("loader")}Planning…`;
  btn.querySelector("svg").style.animation = "spin 1s linear infinite";
  $("#plan-output").innerHTML = `<div class="week">${Array.from({ length: state.planDays }, () => skeletonCard()).join("")}</div>`;
  try {
    state.plan = await api("/api/plan", { method: "POST", body: { ingredients, use_pantry: $("#plan-pantry").checked, preferences: p, days: state.planDays } });
    state.planPrefs = p;
    renderPlan();
  } catch (e) {
    $("#plan-output").innerHTML = `<div class="card">Something went wrong: ${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${icon("calendar")}Plan my week`;
  }
}

function renderPlan() {
  const d = state.plan;
  const days = d.days;
  const avgKcal = Math.round(days.reduce((s, x) => s + x.recipe.nutrition_per_serving.calories, 0) / Math.max(days.length, 1));
  const totalMin = days.reduce((s, x) => s + x.recipe.total_minutes, 0);
  const cuisines = new Set(days.map((x) => x.recipe.cuisine)).size;
  const stat = (ico, lbl, val) => `<div class="stat"><div class="stat-label">${icon(ico)}${lbl}</div><div class="stat-value">${val}</div></div>`;
  $("#plan-output").innerHTML = `
    <div class="plan-summary">
      ${stat("calendar", "Dinners planned", days.length)}
      ${stat("flame", "Avg kcal / serving", avgKcal)}
      ${stat("clock", "Total kitchen time", `${Math.floor(totalMin / 60)}h ${totalMin % 60}m`)}
      ${stat("globe", "Cuisines", cuisines)}
    </div>
    <div class="plan-layout" style="margin-top:18px">
      <div class="week">
        ${days.map((x, k) => {
          const v = visual(x.recipe);
          return `<div class="day" data-day="${k}" style="animation-delay:${k * 60}ms">
            <div class="day-head"><span>${esc(x.day)}</span><span class="muted">${x.recipe.total_minutes} min</span></div>
            <div class="day-art" style="${heroStyle(v)}">${v.emoji}</div>
            <div class="day-body"><span class="rcard-cuisine">${esc(x.recipe.cuisine)}</span><h4>${esc(x.recipe.name)}</h4>
              <div class="meta"><span>${icon("flame")}${x.recipe.nutrition_per_serving.calories} kcal</span><span>${icon("gauge")}${esc(x.recipe.difficulty)}</span></div></div>
          </div>`;
        }).join("")}
      </div>
      <aside class="card side-card">
        ${shoppingCard(d.shopping_list, "Weekly shopping", `${d.shopping_list.length} items`)}
        <div class="side-actions"><button class="btn sm" data-plan-md>${icon("download")}Plan .md</button><button class="btn sm" data-plan-save>${icon("heart")}Save all</button></div>
      </aside>
    </div>`;
}

/* ---------- Cookbook ---------- */

async function loadCookbook() {
  const data = await api(`/api/cookbook?search=${encodeURIComponent($("#cookbook-search").value)}`);
  const s = data.stats;
  const stat = (ico, lbl, val) => `<div class="stat"><div class="stat-label">${icon(ico)}${lbl}</div><div class="stat-value">${val ?? "—"}</div></div>`;
  $("#cookbook-stats").innerHTML =
    stat("book", "Saved recipes", s.count) +
    stat("star", "Average rating", s.avg_rating ? `${s.avg_rating} ★` : null) +
    stat("globe", "Top cuisine", s.top_cuisine) +
    stat("clock", "Avg cook time", s.avg_minutes ? `${s.avg_minutes} min` : null);
  state.cookbook = data.recipes;
  if (!data.recipes.length) {
    $("#cookbook-grid").innerHTML = `<div class="empty" style="grid-column:1/-1"><div class="empty-art">📖</div><h3>No saved recipes yet</h3><p>Tap the heart on any recipe to keep it here.</p></div>`;
    return;
  }
  $("#cookbook-grid").innerHTML = data.recipes
    .map((row, k) => {
      const stars = [1, 2, 3, 4, 5].map((n) => `<button class="${n <= (row.rating || 0) ? "on" : ""}" data-rate="${n}" aria-label="${n} stars">${icon("star")}</button>`).join("");
      const footer = `<div class="rcard-foot"><span class="stars" data-id="${row.id}">${stars}</span><button class="icon-btn" data-del="${row.id}" aria-label="Delete">${icon("trash")}</button></div>`;
      return recipeCard(row.recipe, { footer, idx: k, attr: `data-book="${k}"` });
    })
    .join("");
}

async function refreshSaved() {
  const data = await api("/api/cookbook");
  state.saved = new Map(data.recipes.map((r) => [r.recipe.name, r.id]));
  updateCounts();
}

/* ---------- Pantry ---------- */

async function loadPantry() {
  state.pantry = await api("/api/pantry");
  updateCounts();
}

function renderPantry() {
  $("#pantry-count").textContent = `${state.pantry.length} items`;
  $("#pantry-chips").innerHTML = state.pantry.length
    ? state.pantry.map((p) => `<span class="chip">${esc(p)}<button data-pantry-rm="${esc(p)}" aria-label="Remove">${icon("x")}</button></span>`).join("")
    : `<span class="muted">Your pantry is empty.</span>`;
  $("#pantry-suggest").innerHTML = STAPLES.filter((s) => !state.pantry.includes(s))
    .map((s) => `<button class="quick" data-pantry-add="${esc(s)}">+ ${esc(s)}</button>`)
    .join("");
}

async function pantryAdd(items) {
  state.pantry = await api("/api/pantry", { method: "POST", body: { items } });
  updateCounts();
  renderPantry();
}

function updateCounts() {
  $("#nav-pantry-count").textContent = state.pantry.length || "";
  $("#nav-cookbook-count").textContent = state.saved.size || "";
  $("#pantry-pill").textContent = `(${state.pantry.length})`;
}

/* ---------- History ---------- */

async function loadHistory() {
  const rows = await api("/api/history");
  $("#history-list").innerHTML = rows.length
    ? rows.map((h, k) => `
      <div class="hist-row">
        <div class="hist-when">${esc(new Date(h.created_at).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }))}</div>
        <div class="hist-main">
          <div class="hist-chips">${h.ingredients.map((i) => `<span class="badge">${esc(i)}</span>`).join("")}</div>
          <div class="hist-results">${h.results.map(esc).join(" · ")}</div>
        </div>
        <button class="btn sm ghost" data-rerun="${k}">${icon("refresh")}Run again</button>
      </div>`).join("")
    : `<div class="empty"><div class="empty-art">🕘</div><h3>No searches yet</h3></div>`;
  state.history = rows;
}

/* ---------- Wiring ---------- */

function wire() {
  $("#nav").addEventListener("click", (e) => {
    const b = e.target.closest(".nav-item");
    if (b) go(b.dataset.view);
  });
  $("#menu-btn").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  $("#theme-toggle").addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

  const input = $("#ingredient-input");
  $("#chip-input").addEventListener("click", () => input.focus());
  input.addEventListener("keydown", (e) => {
    if ((e.key === "Enter" || e.key === ",") && input.value.trim()) {
      e.preventDefault();
      addIngredients(input.value);
      input.value = "";
    } else if (e.key === "Enter" && state.ingredients.length) {
      generate();
    } else if (e.key === "Backspace" && !input.value && state.ingredients.length) {
      state.ingredients.pop();
      renderIngredients();
    }
  });
  $("#ingredient-chips").addEventListener("click", (e) => {
    const b = e.target.closest("[data-rm]");
    if (b) { state.ingredients.splice(+b.dataset.rm, 1); renderIngredients(); }
  });
  $("#quick-adds").addEventListener("click", (e) => {
    const b = e.target.closest("[data-add]");
    if (b) addIngredients(b.dataset.add);
  });
  $("#f-allergies").addEventListener("click", (e) => {
    const b = e.target.closest("[data-allergy]");
    if (!b) return;
    const a = b.dataset.allergy;
    state.allergies = state.allergies.includes(a) ? state.allergies.filter((x) => x !== a) : [...state.allergies, a];
    renderAllergies();
  });
  document.querySelectorAll(".stepper[data-target]").forEach((st) =>
    st.addEventListener("click", (e) => {
      const b = e.target.closest("[data-step]");
      if (!b) return;
      state.servings = Math.max(1, Math.min(20, state.servings + Number(b.dataset.step)));
      $("#f-servings").textContent = state.servings;
    })
  );
  const segmented = (sel, cb) =>
    $(sel).addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      $(sel).querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
      cb(Number(b.textContent));
    });
  segmented("#f-count", (n) => (state.count = n));
  segmented("#plan-days", (n) => (state.planDays = n));
  $("#generate-btn").addEventListener("click", generate);

  $("#results").addEventListener("click", (e) => {
    const card = e.target.closest("[data-idx]");
    if (!card) return;
    const r = state.last.recipes[+card.dataset.idx];
    if (e.target.closest("[data-fav]")) {
      saveRecipe(r).then(renderResults);
      return;
    }
    openDrawer(r);
  });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy-list]");
    if (!b) return;
    const items = [...b.closest(".card").querySelectorAll(".shop-list li span")].map((s) => `☐ ${s.textContent}`).join("\n");
    navigator.clipboard?.writeText(items).then(() => toast("Shopping list copied"), () => toast("Copy not available"));
  });

  // Drawer
  $("#drawer-backdrop").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => e.key === "Escape" && closeDrawer());
  $("#drawer").addEventListener("click", async (e) => {
    if (e.target.closest("[data-close]")) return closeDrawer();
    const serv = e.target.closest("[data-serv]");
    if (serv) return scaleDrawer(Number(serv.dataset.serv));
    if (e.target.closest("[data-save]")) {
      await saveRecipe(state.drawer.base);
      renderDrawer();
      if (state.last) renderResults();
      return;
    }
    if (e.target.closest("[data-export]")) return exportRecipe(state.drawer.recipe);
  });

  // Planner
  $("#plan-btn").addEventListener("click", makePlan);
  $("#plan-output").addEventListener("click", async (e) => {
    const day = e.target.closest("[data-day]");
    if (day) return openDrawer(state.plan.days[+day.dataset.day].recipe);
    if (e.target.closest("[data-plan-md]")) return download("meal-plan.md", state.plan.markdown);
    if (e.target.closest("[data-plan-save]")) {
      for (const d of state.plan.days) if (!state.saved.has(d.recipe.name)) await saveRecipe(d.recipe);
      toast(`Saved ${state.plan.days.length} recipes`);
    }
  });

  // Cookbook
  let t;
  $("#cookbook-search").addEventListener("input", () => { clearTimeout(t); t = setTimeout(loadCookbook, 200); });
  $("#cookbook-grid").addEventListener("click", async (e) => {
    const rate = e.target.closest("[data-rate]");
    if (rate) {
      const id = rate.closest("[data-id]").dataset.id;
      await api(`/api/cookbook/${id}`, { method: "PATCH", body: { rating: Number(rate.dataset.rate) } });
      toast(`Rated ${rate.dataset.rate} ★`);
      return loadCookbook();
    }
    const del = e.target.closest("[data-del]");
    if (del) {
      await api(`/api/cookbook/${del.dataset.del}`, { method: "DELETE" });
      await refreshSaved();
      toast("Recipe removed");
      return loadCookbook();
    }
    const card = e.target.closest("[data-book]");
    if (card && !e.target.closest("[data-fav]")) openDrawer(state.cookbook[+card.dataset.book].recipe);
  });

  // Pantry
  const addFromInput = () => {
    const items = $("#pantry-input").value.split(",").map((s) => s.trim()).filter(Boolean);
    if (items.length) pantryAdd(items).then(() => toast(`Added ${items.length} item${items.length === 1 ? "" : "s"}`));
    $("#pantry-input").value = "";
  };
  $("#pantry-add-btn").addEventListener("click", addFromInput);
  $("#pantry-input").addEventListener("keydown", (e) => e.key === "Enter" && addFromInput());
  $("#pantry-suggest").addEventListener("click", (e) => {
    const b = e.target.closest("[data-pantry-add]");
    if (b) pantryAdd([b.dataset.pantryAdd]);
  });
  $("#pantry-chips").addEventListener("click", async (e) => {
    const b = e.target.closest("[data-pantry-rm]");
    if (!b) return;
    state.pantry = await api(`/api/pantry/${encodeURIComponent(b.dataset.pantryRm)}`, { method: "DELETE" });
    updateCounts();
    renderPantry();
  });

  // History
  $("#history-list").addEventListener("click", (e) => {
    const b = e.target.closest("[data-rerun]");
    if (!b) return;
    state.ingredients = [...state.history[+b.dataset.rerun].ingredients];
    $("#use-pantry").checked = false;
    renderIngredients();
    go("discover");
    generate();
  });
}

async function init() {
  initTheme();
  hydrateIcons();
  renderIngredients();
  renderAllergies();
  wire();
  try {
    const s = await api("/api/status");
    $("#status-card").classList.add(s.demo ? "demo" : "live");
    $("#status-title").textContent = s.demo ? "Demo mode" : "Agent online";
    $("#status-sub").textContent = s.demo ? "Sample recipe library · add an API key for live AI" : s.model;
  } catch {
    $("#status-title").textContent = "Server offline";
  }
  await Promise.all([loadPantry(), refreshSaved()]);
  $("#use-pantry").checked = state.pantry.length > 0;
  const view = new URLSearchParams(location.search).get("view");
  if (view && PAGES[view]) go(view);
}

init();
