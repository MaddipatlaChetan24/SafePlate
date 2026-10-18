/* SafePlate app — vanilla JS, no build step. Shared helpers live in common.js. */

const ALLERGIES = ["nuts", "peanut", "dairy", "gluten", "egg", "shellfish", "fish", "soy", "sesame"];
const QUICK = ["paneer", "chickpeas", "spinach", "potatoes", "tomatoes", "onion", "rice", "toor dal", "eggs", "chicken", "cauliflower", "coconut milk"];
const STAPLES = ["rice", "atta", "onion", "tomatoes", "ginger", "garlic", "turmeric", "cumin seeds", "mustard seeds", "ghee", "toor dal", "green chillies", "curry leaves", "garam masala"];

const state = {
  view: "overview",
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
  cookbook: [],
  history: [],
};

const PAGES = { overview: "Overview", discover: "Discover", planner: "Meal Planner", cookbook: "Cookbook", pantry: "Pantry", history: "History" };

function go(view) {
  state.view = view;
  $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  $$(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${view}`));
  $("#crumb").textContent = PAGES[view];
  $("#sidebar").classList.remove("open");
  window.scrollTo({ top: 0 });
  if (view === "overview") loadOverview();
  if (view === "cookbook") loadCookbook();
  if (view === "history") loadHistory();
  if (view === "pantry") renderPantry();
  if (view === "discover") setTimeout(() => $("#ingredient-input").focus(), 50);
}

/* ---------- Overview ---------- */

const kpi = (ico, label, value, sub, glow) =>
  `<div class="kpi" style="--kc:${glow}"><div class="kpi-top"><span class="kpi-label">${label}</span><span class="kpi-ico">${icon(ico)}</span></div><div class="kpi-value">${value}</div><div class="kpi-sub">${sub}</div></div>`;

const ago = (iso) => {
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  return new Date(iso).toLocaleDateString([], { day: "numeric", month: "short" });
};

async function loadOverview() {
  const h = new Date().getHours();
  $("#greeting").textContent = `${h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening"} 👋`;
  const d = await api("/api/overview");
  $("#kpis").innerHTML =
    kpi("search", "Searches run", d.searches, "all time", "var(--glow-2)") +
    kpi("sparkles", "Recipes generated", d.recipes_generated, "every one verified", "var(--glow-1)") +
    kpi("shield", "Issues caught", d.issues_caught, "fixed or removed before display", "var(--glow-3)") +
    kpi("book", "Saved recipes", d.saved, d.avg_rating ? `avg rating ${d.avg_rating} ★` : "rate recipes to personalise", "var(--glow-2)");
  renderColumns($("#chart-week"), d.per_day);
  const weekTotal = d.per_day.reduce((s, x) => s + x.searches, 0);
  $("#ov-week-total").textContent = `${weekTotal} this week`;
  if (d.cuisines.length) {
    renderHBar($("#chart-cuisine"), d.cuisines.map((c, k) => ({ label: c.cuisine, value: c.count, hi: k === 0 })), {
      format: (v) => `${v}`,
      tip: (r) => `<b>${esc(r.label)}</b><span>${r.value} saved recipe${r.value === 1 ? "" : "s"}</span>`,
    });
  } else {
    $("#chart-cuisine").innerHTML = `<div class="empty" style="padding:30px 0"><p>Save recipes to see your favourite regions.</p></div>`;
  }
  $("#ov-recent").innerHTML = d.recent.length
    ? d.recent.map((r) => {
        const v = visual({ name: r.results[0] || "" });
        return `<div class="act-row">
          <div class="act-ico art" style="${artStyle(v)}"><span class="emoji">${v.emoji}</span></div>
          <div class="act-main"><div class="act-title">${esc(r.results.join(" · ") || "No safe recipes")}</div><div class="act-sub">${esc(r.ingredients.join(", ") || "pantry staples")} · ${ago(r.created_at)}</div></div>
          ${r.issues ? `<span class="badge warn">${icon("wrench")}${r.issues} fixed</span>` : `<span class="badge safe">${icon("check")}Verified</span>`}
        </div>`;
      }).join("")
    : `<div class="empty" style="padding:30px 0"><p>No searches yet. Try <b>Cook from pantry</b>.</p></div>`;
  $("#ov-safety").innerHTML = [
    [d.recipes_generated, "recipes verified"],
    [d.issues_caught, "issues caught"],
    ["9", "allergen groups"],
    ["≤ 2", "self-correction retries"],
  ].map(([v, l]) => `<div class="spot-stat"><b>${v}</b><span>${l}</span></div>`).join("");
}

/* Single-series column chart: today highlighted, others in the context grey.
   Only today and the peak are direct-labelled; every column has a tooltip. */
function renderColumns(el, days) {
  const max = Math.max(...days.map((d) => d.searches), 1);
  const top = max <= 4 ? 4 : Math.ceil(max / 4) * 4;
  const peak = days.reduce((a, b) => (b.searches > a.searches ? b : a), days[0]);
  const ticks = [0, top / 2, top];
  el.innerHTML = `
    <div class="col-axis">${ticks.map((t) => `<span style="bottom:${(t / top) * 100}%">${t}</span>`).join("")}</div>
    <div class="col-plot" role="img" aria-label="${esc(days.map((d) => `${d.date}: ${d.searches}`).join("; "))}">
      ${ticks.slice(1).map((t) => `<div class="col-grid" style="bottom:${(t / top) * 100}%"></div>`).join("")}
      ${days.map((d, k) => {
        const day = new Date(d.date + "T00:00").toLocaleDateString([], { weekday: "short" });
        const isToday = k === days.length - 1;
        // Label today (the highlighted column) and the week's peak if it's a different day.
        const label = (isToday || (d === peak && peak !== days[days.length - 1])) && d.searches > 0 ? `<span class="col-val">${d.searches}</span>` : "";
        return `<div class="col ${isToday ? "hi" : ""}" data-k="${k}">${label}<div class="col-bar" style="height:0" data-h="${(d.searches / top) * 100}"></div><span class="col-x">${isToday ? "Today" : day}</span></div>`;
      }).join("")}
    </div>`;
  el.parentElement.classList.add("colchart-wrap");
  requestAnimationFrame(() => $$(".col-bar", el).forEach((b) => (b.style.height = `${b.dataset.h}%`)));
  attachTips(el, ".col", (c) => {
    const d = days[+c.dataset.k];
    return `<b>${new Date(d.date + "T00:00").toLocaleDateString([], { weekday: "long", day: "numeric", month: "short" })}</b><span>${d.searches} search${d.searches === 1 ? "" : "es"}</span>`;
  });
}

/* ---------- Discover ---------- */

function renderIngredients() {
  $("#ingredient-chips").innerHTML = state.ingredients
    .map((i, k) => `<span class="chip">${esc(i)}<button data-rm="${k}" aria-label="Remove ${esc(i)}">${icon("x")}</button></span>`)
    .join("");
  $("#quick-adds").innerHTML = QUICK.filter((q) => !state.ingredients.includes(q))
    .slice(0, 7)
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
  $("#f-allergies").innerHTML = ALLERGIES.map((a) => {
    const on = state.allergies.includes(a);
    return `<button class="toggle-chip ${on ? "on" : ""}" data-allergy="${a}">${on ? icon("x") : ""}${cap(a)}</button>`;
  }).join("");
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

function skeletonCard() {
  return `<div class="rcard skeleton"><div class="art sk" style="height:156px;border-radius:0"></div><div class="rcard-body">
    <div class="sk" style="height:10px;width:35%"></div><div class="sk" style="height:16px;width:85%"></div>
    <div class="sk" style="height:10px;width:60%"></div><div class="sk" style="height:6px"></div></div></div>`;
}

async function generate() {
  const pending = $("#ingredient-input").value.trim();
  if (pending) { addIngredients(pending); $("#ingredient-input").value = ""; }
  const p = prefs();
  const usePantry = $("#use-pantry").checked;
  const total = state.ingredients.length + (usePantry ? state.pantry.filter((x) => !state.ingredients.includes(x)).length : 0);
  const constraints = constraintSummary(p);

  $("#discover-empty").hidden = true;
  $("#results-layout").hidden = false;
  $("#results").innerHTML = Array.from({ length: state.count }, skeletonCard).join("");
  $("#shopping-card").innerHTML = `<div class="sk" style="height:14px;width:55%;margin-bottom:18px"></div>${'<div class="sk" style="height:10px;margin:14px 0"></div>'.repeat(6)}`;
  renderTrace($("#trace"), [
    { state: "done", title: "Read your kitchen", sub: `${total} ingredient${total === 1 ? "" : "s"}${usePantry ? " incl. pantry" : ""}`, icon: "list" },
    { state: "run", title: "Drafting recipes", sub: "Chef + nutritionist prompt", icon: "sparkles" },
    { state: "idle", title: "Safety check", sub: constraints.join(" · ") || "No hard constraints", icon: "shield" },
    { state: "idle", title: "Verified", sub: "Ready to cook", icon: "check" },
  ]);
  const btn = $("#generate-btn");
  btn.disabled = true;
  btn.innerHTML = `${icon("loader")}Generating…`;
  btn.querySelector("svg").style.animation = "spin 1s linear infinite";

  try {
    const [data] = await Promise.all([
      api("/api/suggest", { method: "POST", body: { ingredients: state.ingredients, use_pantry: usePantry, preferences: p, count: state.count } }),
      new Promise((r) => setTimeout(r, 650)),
    ]);
    state.last = data;
    state.lastPrefs = p;
    const fixes = data.trace.corrections.length;
    renderTrace($("#trace"), [
      { state: "done", title: "Read your kitchen", sub: `${data.ingredients.length} ingredients${usePantry ? " incl. pantry" : ""}`, icon: "list" },
      { state: "done", title: `Drafted ${data.recipes.length} recipe${data.recipes.length === 1 ? "" : "s"}`, sub: `${data.trace.attempts} LLM call${data.trace.attempts === 1 ? "" : "s"}`, icon: "sparkles" },
      fixes
        ? { state: "fixed", title: `Self-corrected ${fixes} issue${fixes === 1 ? "" : "s"}`, sub: data.trace.corrections[0], icon: "shield" }
        : { state: "done", title: "Safety check passed", sub: constraints.join(" · ") || "No hard constraints", icon: "shield" },
      { state: "done", title: "Verified", sub: `${data.recipes.length} safe to cook`, icon: "check" },
    ]);
    renderResults();
  } catch (e) {
    $("#results").innerHTML = `<div class="panel glass">Something went wrong: ${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${icon("sparkles")}Generate recipes`;
  }
}

function recipeCard(r, { recommended = false, prefsUsed = null, footer = "", idx = 0, attr = "" } = {}) {
  const v = visual(r);
  const n = r.nutrition_per_serving;
  const used = (r.uses || []).length;
  const pct = Math.round((used / Math.max(r.ingredients.length, 1)) * 100);
  const tags = prefsUsed ? constraintSummary(prefsUsed).map((t) => `<span class="badge safe">${icon("check")}${esc(t)}</span>`) : [];
  tags.push(r.missing_ingredients.length
    ? `<span class="badge warn">${icon("cart")}Buy ${r.missing_ingredients.length}</span>`
    : `<span class="badge safe">${icon("check")}Nothing to buy</span>`);
  const saved = state.saved.has(r.name);
  return `
    <article class="rcard" ${attr} style="animation-delay:${idx * 70}ms">
      <div class="art" style="${artStyle(v)}">
        <div class="rcard-flags">
          ${recommended ? `<span class="pill-glass">${icon("sparkles")}Best match</span>` : `<span class="pill-glass safe">${icon("shield")}Verified</span>`}
          <button class="fav ${saved ? "on" : ""}" data-fav aria-label="Save">${icon("heart")}</button>
        </div>
        <span class="emoji">${v.emoji}</span>
      </div>
      <div class="rcard-body">
        <div><div class="rcard-cuisine">${esc(r.cuisine)}</div><div class="rcard-title">${esc(r.name)}</div></div>
        <div class="meta"><span>${icon("clock")}${r.total_minutes} min</span><span>${icon("flame")}${n.calories} kcal</span><span>${icon("gauge")}${esc(r.difficulty)}</span></div>
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
  $("#results").innerHTML = d.recipes.length
    ? d.recipes.map((r, k) => recipeCard(r, { recommended: r.name === d.recommended, prefsUsed: state.lastPrefs, idx: k, attr: `data-idx="${k}"` })).join("")
    : `<div class="panel glass">No recipe could satisfy every constraint. Try relaxing the time limit or adding ingredients.</div>`;
  $("#shopping-card").innerHTML = shoppingCard(d.shopping_list, "Shopping list", `${d.recipes.length} recipes`);
}

function shoppingCard(items, title, sub) {
  const body = items.length
    ? `<ul class="shop-list">${items.map((i) => `<li><input type="checkbox" /><span>${esc(i.label)}</span></li>`).join("")}</ul>
       <div class="side-actions"><button class="btn sm" data-copy-list>${icon("copy")}Copy list</button></div>`
    : `<div class="pill-ok">${icon("check")}You have everything</div>`;
  return `<div class="panel-head"><h3>${icon("cart")}${esc(title)}</h3><span class="badge">${esc(sub)}</span></div>${body}`;
}

/* ---------- Drawer ---------- */

function openDrawer(recipe, ctx = {}) {
  state.drawer = { recipe, ctx, base: recipe };
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

function label(i) {
  if (i.quantity == null) return `${i.name} (to taste)`;
  const q = Number.isInteger(i.quantity) ? i.quantity : +i.quantity.toFixed(2);
  return `${q} ${i.unit || ""} ${i.name}`.replace(/\s+/g, " ").trim();
}

function renderDrawer() {
  const r = state.drawer.recipe;
  const v = visual(r);
  const n = r.nutrition_per_serving;
  const kc = { p: n.protein_g * 4, c: n.carbs_g * 4, f: n.fat_g * 9 };
  const tot = kc.p + kc.c + kc.f || 1;
  const a1 = (kc.p / tot) * 360, a2 = a1 + (kc.c / tot) * 360;
  const gap = 2; // surface gap between donut segments, in degrees
  const donut = `conic-gradient(var(--protein) 0 ${a1 - gap}deg, var(--surface-solid) ${a1 - gap}deg ${a1}deg, var(--carbs) ${a1}deg ${a2 - gap}deg, var(--surface-solid) ${a2 - gap}deg ${a2}deg, var(--fat) ${a2}deg ${360 - gap}deg, var(--surface-solid) ${360 - gap}deg 360deg)`;
  const missing = new Set(r.missing_ingredients.map((i) => i.name));
  const uses = new Set(r.uses || []);
  const ingRow = (i) => {
    const kind = uses.has(i.name) ? "have" : missing.has(i.name) ? "buy" : "base";
    return `<li><span class="ing-dot ${kind}">${icon(kind === "have" ? "check" : kind === "buy" ? "plus" : "box")}</span><span>${esc(label(i))}</span></li>`;
  };
  const maxMacro = Math.max(n.protein_g, n.carbs_g, n.fat_g, 1);
  const macro = (name, val, color) =>
    `<div class="macro" style="--c:${color}"><span><i class="swatch"></i>${name}</span><div class="bar"><i style="width:${(val / maxMacro) * 100}%"></i></div><b>${val}g</b></div>`;
  const saved = state.saved.has(r.name);

  $("#drawer").innerHTML = `
    <div class="art d-hero" style="${artStyle(v)}">
      <button class="icon-btn d-close" data-close aria-label="Close">${icon("x")}</button>
      <span class="emoji">${v.emoji}</span>
    </div>
    <div class="d-body">
      <div class="d-title">
        <div class="rcard-cuisine">${esc(r.cuisine)} · ${esc(r.difficulty)}</div>
        <h2>${esc(r.name)}</h2>
        <div class="meta"><span>${icon("clock")}Prep ${r.prep_minutes} min</span><span>${icon("flame")}Cook ${r.cook_minutes} min</span><span>${icon("users")}Serves ${r.servings}</span><span class="badge safe">${icon("shield")}Verified</span></div>
      </div>
      <div class="d-bar">
        <div style="display:flex;align-items:center;gap:10px"><span class="fld-label">Servings</span>
          <div class="stepper"><button data-serv="-1">−</button><span>${r.servings}</span><button data-serv="1">+</button></div></div>
        <div class="d-actions">
          <button class="btn ${saved ? "" : "primary"}" data-save>${icon("heart")}${saved ? "Saved" : "Save"}</button>
          <button class="btn" data-export>${icon("download")}Markdown</button>
        </div>
      </div>
      <div class="d-cols">
        <div class="d-section"><h3>Ingredients</h3><ul class="ing-list">${r.ingredients.map(ingRow).join("")}</ul>
          <div style="display:flex;gap:14px;margin-top:12px" class="small muted"><span><span class="ing-dot have">${icon("check")}</span> on hand</span><span><span class="ing-dot buy">${icon("plus")}</span> to buy</span></div></div>
        <div class="d-section"><h3>Method</h3><ol class="steps">${r.instructions.map((s) => `<li><span>${esc(s.replace(/^step\s*\d+[:.]\s*/i, ""))}</span></li>`).join("")}</ol></div>
      </div>
      <div class="d-section"><h3>Nutrition per serving</h3>
        <div class="nutri">
          <div class="donut" style="background:${donut}" role="img" aria-label="Protein ${n.protein_g} g, carbs ${n.carbs_g} g, fat ${n.fat_g} g"><div class="donut-inner"><div><b>${n.calories}</b><br><span>kcal</span></div></div></div>
          <div class="macros">${macro("Protein", n.protein_g, "var(--protein)")}${macro("Carbs", n.carbs_g, "var(--carbs)")}${macro("Fat", n.fat_g, "var(--fat)")}</div>
        </div>
      </div>
      ${r.substitutions.length ? `<div class="d-section"><h3>Smart swaps</h3><div class="swaps">${r.substitutions.map((s) => `<span class="swap">${esc(s.replace("->", "→"))}</span>`).join("")}</div></div>` : ""}
      ${r.tips ? `<div class="callout">${icon("bulb")}<div><b>Chef's tip.</b> ${esc(r.tips)}</div></div>` : ""}
    </div>`;
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

function download(name, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ---------- Planner ---------- */

async function makePlan() {
  const p = prefs();
  const ingredients = $("#plan-ingredients").value.split(",").map((s) => s.trim()).filter(Boolean);
  const btn = $("#plan-btn");
  btn.disabled = true;
  btn.innerHTML = `${icon("loader")}Planning…`;
  btn.querySelector("svg").style.animation = "spin 1s linear infinite";
  $("#plan-output").innerHTML = `<div class="week">${Array.from({ length: state.planDays }, skeletonCard).join("")}</div>`;
  try {
    state.plan = await api("/api/plan", { method: "POST", body: { ingredients, use_pantry: $("#plan-pantry").checked, preferences: p, days: state.planDays } });
    renderPlan();
  } catch (e) {
    $("#plan-output").innerHTML = `<div class="panel glass">Something went wrong: ${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${icon("calendar")}Plan my week`;
  }
}

function renderPlan() {
  const days = state.plan.days;
  const avgKcal = Math.round(days.reduce((s, x) => s + x.recipe.nutrition_per_serving.calories, 0) / Math.max(days.length, 1));
  const totalMin = days.reduce((s, x) => s + x.recipe.total_minutes, 0);
  const regions = new Set(days.map((x) => x.recipe.cuisine)).size;
  $("#plan-output").innerHTML = `
    <div class="kpis">
      ${kpi("calendar", "Dinners planned", days.length, "one per day", "var(--glow-1)")}
      ${kpi("flame", "Avg kcal / serving", avgKcal, "across the week", "var(--glow-2)")}
      ${kpi("clock", "Kitchen time", `${Math.floor(totalMin / 60)}h ${totalMin % 60}m`, "prep + cook, total", "var(--glow-3)")}
      ${kpi("globe", "Regions", regions, "different regional cuisines", "var(--glow-2)")}
    </div>
    <div class="plan-layout" style="margin-top:18px">
      <div class="week">
        ${days.map((x, k) => {
          const v = visual(x.recipe);
          return `<div class="day" data-day="${k}" style="animation-delay:${k * 60}ms">
            <div class="day-head"><span>${esc(x.day)}</span><span class="muted">${x.recipe.total_minutes} min</span></div>
            <div class="art" style="${artStyle(v)}"><span class="emoji">${v.emoji}</span></div>
            <div class="day-body"><span class="rcard-cuisine">${esc(x.recipe.cuisine)}</span><h4>${esc(x.recipe.name)}</h4>
              <div class="meta"><span>${icon("flame")}${x.recipe.nutrition_per_serving.calories} kcal</span><span>${icon("gauge")}${esc(x.recipe.difficulty)}</span></div></div>
          </div>`;
        }).join("")}
      </div>
      <aside class="panel glass side">
        ${shoppingCard(state.plan.shopping_list, "Weekly shopping", `${state.plan.shopping_list.length} items`)}
        <div class="side-actions"><button class="btn sm" data-plan-md>${icon("download")}Plan .md</button><button class="btn sm" data-plan-save>${icon("heart")}Save all</button></div>
      </aside>
    </div>`;
}

/* ---------- Cookbook ---------- */

async function loadCookbook() {
  const data = await api(`/api/cookbook?search=${encodeURIComponent($("#cookbook-search").value)}`);
  const s = data.stats;
  $("#cookbook-stats").innerHTML =
    kpi("book", "Saved recipes", s.count, "in your cookbook", "var(--glow-1)") +
    kpi("star", "Average rating", s.avg_rating ? `${s.avg_rating} ★` : "—", "from your ratings", "var(--glow-2)") +
    kpi("globe", "Top region", s.top_cuisine ?? "—", "most saved", "var(--glow-3)") +
    kpi("clock", "Avg cook time", s.avg_minutes ? `${s.avg_minutes} min` : "—", "prep + cook", "var(--glow-2)");
  state.cookbook = data.recipes;
  $("#cookbook-grid").innerHTML = data.recipes.length
    ? data.recipes.map((row, k) => {
        const stars = [1, 2, 3, 4, 5].map((n) => `<button class="${n <= (row.rating || 0) ? "on" : ""}" data-rate="${n}" aria-label="${n} stars">${icon("star")}</button>`).join("");
        const footer = `<div class="rcard-foot"><span class="stars" data-id="${row.id}">${stars}</span><button class="icon-btn" data-del="${row.id}" aria-label="Delete">${icon("trash")}</button></div>`;
        return recipeCard(row.recipe, { footer, idx: k, attr: `data-book="${k}"` });
      }).join("")
    : `<div class="empty" style="grid-column:1/-1"><div class="empty-art">📖</div><h3>No saved recipes yet</h3><p>Tap the heart on any recipe to keep it here.</p></div>`;
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
    .map((s) => `<button class="quick" data-pantry-add="${esc(s)}">+ ${esc(s)}</button>`).join("");
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
  state.history = rows;
  $("#history-list").innerHTML = rows.length
    ? rows.map((h, k) => `
      <div class="hist-row">
        <div class="hist-when">${esc(new Date(h.created_at).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }))}</div>
        <div class="hist-main">
          <div class="hist-chips">${h.ingredients.map((i) => `<span class="badge">${esc(i)}</span>`).join("")}</div>
          <div class="hist-results">${h.results.map(esc).join(" · ")}</div>
        </div>
        ${h.issues ? `<span class="badge warn">${icon("wrench")}${h.issues} fixed</span>` : `<span class="badge safe">${icon("check")}Verified</span>`}
        <button class="btn sm ghost" data-rerun="${k}">${icon("refresh")}Run again</button>
      </div>`).join("")
    : `<div class="empty"><div class="empty-art">🕘</div><h3>No searches yet</h3></div>`;
}

/* ---------- Command palette ---------- */

const palette = { items: [], sel: 0 };

function paletteItems(q) {
  const nav = Object.entries(PAGES).map(([v, name]) => ({ group: "Go to", label: name, icon: { overview: "grid", discover: "sparkles", planner: "calendar", cookbook: "book", pantry: "box", history: "clock" }[v], run: () => go(v) }));
  const actions = [
    { group: "Actions", label: "Cook from pantry", icon: "sparkles", hint: "generate", run: cookFromPantry },
    { group: "Actions", label: "Plan my week", icon: "calendar", run: () => { go("planner"); makePlan(); } },
    { group: "Actions", label: "Toggle theme", icon: "moon", run: toggleTheme },
  ];
  const term = q.trim().toLowerCase();
  let items = [...actions, ...nav].filter((i) => !term || i.label.toLowerCase().includes(term));
  if (term) {
    items = [
      { group: "Ingredients", label: `Find recipes with “${q.trim()}”`, icon: "search", hint: "↵", run: () => { state.ingredients = []; addIngredients(q); go("discover"); generate(); } },
      { group: "Ingredients", label: `Add “${q.trim()}” to pantry`, icon: "plus", run: () => pantryAdd(q.split(",")).then(() => toast("Added to pantry")) },
      ...items,
    ];
  }
  return items;
}

function renderPalette() {
  const q = $("#palette-input").value;
  palette.items = paletteItems(q);
  palette.sel = Math.min(palette.sel, Math.max(palette.items.length - 1, 0));
  let group = "";
  $("#palette-list").innerHTML = palette.items.map((it, k) => {
    const head = it.group !== group ? `<div class="p-group">${esc((group = it.group))}</div>` : "";
    return `${head}<button class="p-item ${k === palette.sel ? "sel" : ""}" data-p="${k}">${icon(it.icon)}<span>${esc(it.label)}</span>${it.hint ? `<span class="p-hint">${esc(it.hint)}</span>` : ""}</button>`;
  }).join("") || `<div class="p-group">No results</div>`;
}

function openPalette() {
  $("#palette").hidden = false;
  $("#palette-input").value = "";
  palette.sel = 0;
  renderPalette();
  $("#palette-input").focus();
}
function closePalette() { $("#palette").hidden = true; }
function runPalette(k) {
  const it = palette.items[k];
  if (!it) return;
  closePalette();
  it.run();
}

function cookFromPantry() {
  $("#use-pantry").checked = true;
  go("discover");
  generate();
}

/* ---------- Wiring ---------- */

function wire() {
  $$(".nav").forEach((n) => n.addEventListener("click", (e) => { const b = e.target.closest(".nav-item"); if (b) go(b.dataset.view); }));
  document.addEventListener("click", (e) => {
    const g = e.target.closest("[data-go]");
    if (g) go(g.dataset.go);
    if (e.target.closest("[data-quick-pantry]")) cookFromPantry();
    const copy = e.target.closest("[data-copy-list]");
    if (copy) {
      const items = $$(".shop-list li span", copy.closest(".panel")).map((s) => `☐ ${s.textContent}`).join("\n");
      navigator.clipboard?.writeText(items).then(() => toast("Shopping list copied"), () => toast("Copy not available"));
    }
  });
  $("#menu-btn").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  $("#theme-toggle").addEventListener("click", toggleTheme);
  $("#new-search").addEventListener("click", () => { state.ingredients = []; renderIngredients(); go("discover"); });
  $("#open-palette").addEventListener("click", openPalette);

  // Keyboard
  document.addEventListener("keydown", (e) => {
    const typing = /input|textarea|select/i.test(document.activeElement?.tagName || "");
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); $("#palette").hidden ? openPalette() : closePalette(); return; }
    if (e.key === "Escape") { closePalette(); closeDrawer(); return; }
    if (!$("#palette").hidden) {
      if (e.key === "ArrowDown") { e.preventDefault(); palette.sel = (palette.sel + 1) % palette.items.length; renderPalette(); }
      if (e.key === "ArrowUp") { e.preventDefault(); palette.sel = (palette.sel - 1 + palette.items.length) % palette.items.length; renderPalette(); }
      if (e.key === "Enter") { e.preventDefault(); runPalette(palette.sel); }
      return;
    }
    if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "d") go("discover");
    if (e.key === "p") go("planner");
  });
  $("#palette-input").addEventListener("input", () => { palette.sel = 0; renderPalette(); });
  $("#palette-list").addEventListener("click", (e) => { const b = e.target.closest("[data-p]"); if (b) runPalette(+b.dataset.p); });
  $("#palette").addEventListener("click", (e) => { if (e.target.id === "palette") closePalette(); });

  // Discover
  const input = $("#ingredient-input");
  $("#chip-input").addEventListener("click", (e) => {
    const b = e.target.closest("[data-rm]");
    if (b) { state.ingredients.splice(+b.dataset.rm, 1); renderIngredients(); return; }
    input.focus();
  });
  input.addEventListener("keydown", (e) => {
    if ((e.key === "Enter" || e.key === ",") && input.value.trim()) { e.preventDefault(); addIngredients(input.value); input.value = ""; }
    else if (e.key === "Enter" && state.ingredients.length) generate();
    else if (e.key === "Backspace" && !input.value && state.ingredients.length) { state.ingredients.pop(); renderIngredients(); }
  });
  $("#quick-adds").addEventListener("click", (e) => { const b = e.target.closest("[data-add]"); if (b) addIngredients(b.dataset.add); });
  $("#f-allergies").addEventListener("click", (e) => {
    const b = e.target.closest("[data-allergy]");
    if (!b) return;
    const a = b.dataset.allergy;
    state.allergies = state.allergies.includes(a) ? state.allergies.filter((x) => x !== a) : [...state.allergies, a];
    renderAllergies();
  });
  $(".composer .stepper").addEventListener("click", (e) => {
    const b = e.target.closest("[data-step]");
    if (!b) return;
    state.servings = Math.max(1, Math.min(20, state.servings + Number(b.dataset.step)));
    $("#f-servings").textContent = state.servings;
  });
  const segmented = (sel, cb) => $(sel).addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    $$("button", $(sel)).forEach((x) => x.classList.toggle("on", x === b));
    cb(Number(b.textContent));
  });
  segmented("#f-count", (n) => (state.count = n));
  segmented("#plan-days", (n) => (state.planDays = n));
  $("#generate-btn").addEventListener("click", generate);
  $("#results").addEventListener("click", (e) => {
    const card = e.target.closest("[data-idx]");
    if (!card) return;
    const r = state.last.recipes[+card.dataset.idx];
    if (e.target.closest("[data-fav]")) { saveRecipe(r).then(renderResults); return; }
    openDrawer(r);
  });

  // Drawer
  $("#drawer-backdrop").addEventListener("click", closeDrawer);
  $("#drawer").addEventListener("click", async (e) => {
    if (e.target.closest("[data-close]")) return closeDrawer();
    const serv = e.target.closest("[data-serv]");
    if (serv) return scaleDrawer(Number(serv.dataset.serv));
    if (e.target.closest("[data-save]")) { await saveRecipe(state.drawer.base); renderDrawer(); if (state.last) renderResults(); return; }
    if (e.target.closest("[data-export]")) {
      const md = await api("/api/export/markdown", { method: "POST", body: state.drawer.recipe });
      download(`${slug(state.drawer.recipe.name)}.md`, md);
    }
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
      await api(`/api/cookbook/${rate.closest("[data-id]").dataset.id}`, { method: "PATCH", body: { rating: Number(rate.dataset.rate) } });
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
  $("#pantry-suggest").addEventListener("click", (e) => { const b = e.target.closest("[data-pantry-add]"); if (b) pantryAdd([b.dataset.pantryAdd]); });
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
  hydrateIcons();
  renderIngredients();
  renderAllergies();
  wire();
  try {
    const s = await api("/api/status");
    $("#mode-card").classList.add(s.demo ? "demo" : "live");
    $("#mode-title").textContent = s.demo ? "Demo mode" : "Agent online";
    $("#mode-sub").textContent = s.demo ? "Curated library of 14 Indian dishes. Add an API key for live AI." : `Model: ${s.model}`;
  } catch {
    $("#mode-title").textContent = "Server offline";
  }
  $("#mode-safety").textContent = "Safety layer active · 9 allergen groups";
  requestAnimationFrame(() => ($("#mode-meter").style.width = "100%"));
  await Promise.all([loadPantry(), refreshSaved()]);
  $("#use-pantry").checked = state.pantry.length > 0;
  const view = new URLSearchParams(location.search).get("view");
  go(view && PAGES[view] ? view : "overview");
}

init();
