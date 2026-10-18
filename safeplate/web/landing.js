/* Landing page: live demo + results charts. */

const DEMO_ALLERGIES = ["nuts", "dairy", "gluten", "egg", "shellfish", "fish", "soy"];
const demo = { ingredients: ["chicken", "tomatoes", "onion", "ginger", "garlic", "rice"], allergies: ["nuts"] };

function renderDemoChips() {
  $("#d-chips").innerHTML = demo.ingredients
    .map((i, k) => `<span class="chip">${esc(i)}<button data-rm="${k}" aria-label="Remove ${esc(i)}">${icon("x")}</button></span>`)
    .join("");
  $("#d-allergies").innerHTML = DEMO_ALLERGIES.map((a) => {
    const on = demo.allergies.includes(a);
    return `<button class="toggle-chip ${on ? "on" : ""}" data-a="${a}">${on ? icon("x") : ""}${cap(a)}</button>`;
  }).join("");
}

async function runDemo() {
  const pending = $("#d-input").value.trim();
  if (pending) { demo.ingredients.push(...pending.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean)); $("#d-input").value = ""; renderDemoChips(); }
  const prefs = { diet: $("#d-diet").value, allergies: [...demo.allergies], servings: 2 };
  const constraints = constraintSummary(prefs);
  const btn = $("#d-run");
  btn.disabled = true;
  btn.innerHTML = `${icon("loader")}Generating…`;
  btn.querySelector("svg").style.animation = "spin 1s linear infinite";
  renderTrace($("#d-trace"), [
    { state: "done", title: "Read kitchen", sub: `${demo.ingredients.length} ingredients`, icon: "list" },
    { state: "run", title: "Drafting recipes", sub: "Structured output", icon: "sparkles" },
    { state: "idle", title: "Safety check", sub: constraints.join(" · ") || "No constraints", icon: "shield" },
    { state: "idle", title: "Verified", sub: "Ready to cook", icon: "check" },
  ]);
  $("#d-results").innerHTML = Array.from({ length: 3 }, () => `<div class="res-row"><div class="sk" style="width:64px;height:64px;border-radius:12px"></div><div class="res-main"><div class="sk" style="height:14px;width:55%"></div><div class="sk" style="height:10px;width:35%"></div></div></div>`).join("");

  try {
    const [data] = await Promise.all([
      api("/api/suggest", { method: "POST", body: { ingredients: demo.ingredients, preferences: prefs, count: 3 } }),
      new Promise((r) => setTimeout(r, 700)),
    ]);
    const fixes = data.trace.corrections.length;
    renderTrace($("#d-trace"), [
      { state: "done", title: "Read kitchen", sub: `${data.ingredients.length} ingredients`, icon: "list" },
      { state: "done", title: `Drafted ${data.recipes.length} recipes`, sub: `${data.trace.attempts} LLM call${data.trace.attempts === 1 ? "" : "s"}`, icon: "sparkles" },
      fixes
        ? { state: "fixed", title: `Fixed ${fixes} issue${fixes === 1 ? "" : "s"}`, sub: data.trace.corrections[0], icon: "shield" }
        : { state: "done", title: "Safety check passed", sub: constraints.join(" · ") || "No constraints", icon: "shield" },
      { state: "done", title: "Verified", sub: `${data.recipes.length} safe to cook`, icon: "check" },
    ]);
    $("#d-results").innerHTML = data.recipes.map((r, k) => {
      const v = visual(r);
      const pct = Math.round(((r.uses || []).length / Math.max(r.ingredients.length, 1)) * 100);
      const badges = constraints.map((c) => `<span class="badge safe">${icon("check")}${esc(c)}</span>`).join("");
      return `<div class="res-row" style="animation-delay:${k * 80}ms">
        <div class="art" style="${artStyle(v)}"><span class="emoji">${v.emoji}</span></div>
        <div class="res-main">
          <div class="res-title">${esc(r.name)}${r.name === data.recommended ? `<span class="badge brand">${icon("sparkles")}Best match</span>` : ""}</div>
          <div class="res-meta"><span>${icon("globe")}${esc(r.cuisine)}</span><span>${icon("clock")}${r.total_minutes} min</span><span>${icon("flame")}${r.nutrition_per_serving.calories} kcal</span></div>
          ${badges ? `<div class="res-badges">${badges}</div>` : ""}
        </div>
        <div class="res-match"><span class="muted small">On hand</span><br /><b>${pct}%</b><div class="bar"><i style="width:${pct}%"></i></div></div>
      </div>`;
    }).join("") + `<div class="res-foot"><span class="muted small">${data.shopping_list.length} item${data.shopping_list.length === 1 ? "" : "s"} to buy across all recipes</span><a class="btn sm" href="/app">Open full recipes in the app ${icon("arrow")}</a></div>`;
  } catch (e) {
    $("#d-results").innerHTML = `<div class="res-row">Could not reach the API: ${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${icon("sparkles")}Generate`;
  }
}

function renderCharts() {
  // results/self_correction_sim.csv, p_violate = 0.3
  renderHBar($("#chart-unsafe"), [
    { label: "Trust the LLM", value: 30.43 },
    { label: "Check + drop", value: 8.0 },
    { label: "Check + 1 retry", value: 6.1 },
    { label: "SafePlate (2 retries)", value: 5.85, hi: true },
  ], {
    max: 32,
    format: (v) => `${v.toFixed(1)}%`,
    tip: (r) => `<b>${esc(r.label)}</b><span>${r.value.toFixed(2)}% of shown recipes contained an allergen</span>`,
  });
  // results/allergen_benchmark_summary_v1_frozen.csv
  renderHBar($("#chart-f1"), [
    { label: "Naive substring", value: 0.68, fp: 25 },
    { label: "Word boundary", value: 0.721, fp: 16 },
    { label: "SafePlate", value: 0.827, fp: 5, hi: true },
  ], {
    max: 1,
    format: (v) => v.toFixed(3),
    tip: (r) => `<b>${esc(r.label)}</b><span>F1 ${r.value.toFixed(3)} · ${r.fp} false alarms</span>`,
  });
}

function initLanding() {
  hydrateIcons();
  renderDemoChips();
  renderCharts();
  $("#theme-toggle").addEventListener("click", toggleTheme);
  $("#d-chips-box").addEventListener("click", (e) => {
    const rm = e.target.closest("[data-rm]");
    if (rm) { demo.ingredients.splice(+rm.dataset.rm, 1); renderDemoChips(); return; }
    $("#d-input").focus();
  });
  $("#d-input").addEventListener("keydown", (e) => {
    const input = e.target;
    if ((e.key === "Enter" || e.key === ",") && input.value.trim()) {
      e.preventDefault();
      demo.ingredients.push(...input.value.split(",").map((s) => s.trim().toLowerCase()).filter((s) => s && !demo.ingredients.includes(s)));
      input.value = "";
      renderDemoChips();
    } else if (e.key === "Enter") {
      runDemo();
    } else if (e.key === "Backspace" && !input.value && demo.ingredients.length) {
      demo.ingredients.pop();
      renderDemoChips();
    }
  });
  $("#d-allergies").addEventListener("click", (e) => {
    const b = e.target.closest("[data-a]");
    if (!b) return;
    const a = b.dataset.a;
    demo.allergies = demo.allergies.includes(a) ? demo.allergies.filter((x) => x !== a) : [...demo.allergies, a];
    renderDemoChips();
  });
  $("#d-run").addEventListener("click", runDemo);
  api("/api/status").then((s) => {
    const b = $("#mode-badge");
    b.className = `badge ${s.demo ? "warn" : "safe"}`;
    b.textContent = s.demo ? "Demo mode · sample library" : `Live · ${s.model}`;
  }).catch(() => ($("#mode-badge").textContent = "API offline"));
  if (new URLSearchParams(location.search).has("autorun")) runDemo();
}

initLanding();
