/* Shared helpers for the SafePlate landing page and app. */

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
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  github: '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
  terminal: '<path d="m4 17 6-6-6-6M12 19h8"/>',
  scale: '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1ZM2 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  command: '<path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3"/>',
  logo: '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="5.5" stroke-opacity=".55"/><path d="m9.6 12.1 1.7 1.7 3.2-3.5"/>',
};
const icon = (name, cls = "i") =>
  `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;

function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    el.outerHTML = icon(el.dataset.icon, ["i", ...el.classList].join(" "));
  });
}

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

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
  const box = $("#toasts");
  if (!box) return;
  const el = document.createElement("div");
  el.className = "toast";
  el.innerHTML = `${icon("check")}<span>${esc(msg)}</span>`;
  box.appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

/* Theme: warm light by default; ?theme= overrides for screenshots. */
function initTheme() {
  let theme = null;
  try { theme = localStorage.getItem("sp-theme"); } catch {}
  theme = new URLSearchParams(location.search).get("theme") || theme || "light";
  document.documentElement.dataset.theme = theme;
}
function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("sp-theme", next); } catch {}
}

/* Dish art: emoji + two mesh-gradient colours, chosen from the recipe name. */
const VISUALS = [
  [/biryani|pulao/i, "🍚", "#f59e0b", "#ef4444"],
  [/butter chicken|tikka|chicken/i, "🍗", "#fb923c", "#ef4444"],
  [/palak|saag|spinach/i, "🥬", "#22c55e", "#84cc16"],
  [/chana|rajma|chole/i, "🫘", "#f97316", "#b45309"],
  [/dal|sambar|soup|rasam/i, "🍲", "#facc15", "#f97316"],
  [/fish|meen|prawn|salmon/i, "🐟", "#38bdf8", "#14b8a6"],
  [/egg|bhurji|anda|omelet/i, "🍳", "#facc15", "#fb923c"],
  [/poha|upma|khichdi/i, "🥣", "#fde047", "#a3e635"],
  [/lemon rice|curd rice|rice/i, "🍋", "#fde047", "#facc15"],
  [/pav|vada|roll/i, "🍞", "#f97316", "#facc15"],
  [/aloo|gobi|sabzi|thoran/i, "🥔", "#f59e0b", "#eab308"],
  [/paneer|kadai|masala|curry|korma/i, "🍛", "#f97316", "#ec4899"],
  [/dosa|idli|uttapam/i, "🫓", "#fbbf24", "#f97316"],
];
function visual(r) {
  for (const [re, emoji, c1, c2] of VISUALS) if (re.test(r.name)) return { emoji, c1, c2 };
  return { emoji: "🍽️", c1: "#a78bfa", c2: "#f472b6" };
}
const artStyle = (v) => `--c1:${v.c1};--c2:${v.c2}`;

function constraintSummary(p) {
  const parts = [];
  if (p.diet) parts.push(cap(p.diet));
  (p.allergies || []).forEach((a) => parts.push(`${cap(a === "nuts" ? "nut" : a)}-free`));
  if (p.max_minutes) parts.push(`≤ ${p.max_minutes} min`);
  return parts;
}

function renderTrace(el, steps) {
  el.hidden = false;
  el.innerHTML = steps
    .map((s, k) => {
      const ico = s.state === "run" ? "loader" : s.state === "fixed" ? "wrench" : s.state === "done" ? "check" : s.icon;
      const line = k < steps.length - 1 ? `<div class="trace-line ${s.state === "done" || s.state === "fixed" ? "done" : ""}"></div>` : "";
      return `<div class="trace-step ${s.state}"><div class="trace-ico">${icon(ico)}</div><div style="min-width:0"><div class="trace-title">${esc(s.title)}</div><div class="trace-sub" title="${esc(s.sub)}">${esc(s.sub)}</div></div></div>${line}`;
    })
    .join("");
}

/* Horizontal bar chart: one series, the highlighted row in the accent, others in the context grey.
   Every bar is direct-labelled (values at the tip) and has a hover tooltip. */
function renderHBar(el, rows, { max, format = (v) => v, tip = () => "" } = {}) {
  const top = max ?? Math.max(...rows.map((r) => r.value), 1);
  el.classList.add("hbar");
  el.setAttribute("role", "img");
  el.innerHTML = rows
    .map((r, k) => `
      <div class="hbar-row ${r.hi ? "hi" : ""}" data-k="${k}">
        <div class="hbar-label">${esc(r.label)}</div>
        <div class="hbar-track"><div class="hbar-bar" style="width:0%" data-w="${(r.value / top) * 100}"></div><span class="hbar-val">${esc(format(r.value))}</span></div>
      </div>`)
    .join("");
  el.setAttribute("aria-label", rows.map((r) => `${r.label}: ${format(r.value)}`).join("; "));
  requestAnimationFrame(() => $$(".hbar-bar", el).forEach((b) => (b.style.width = `${Math.max(+b.dataset.w, 0.4)}%`)));
  attachTips(el, ".hbar-row", (row) => tip(rows[+row.dataset.k]));
}

let tipEl;
function attachTips(root, selector, html) {
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.className = "tip";
    document.body.appendChild(tipEl);
  }
  root.addEventListener("mousemove", (e) => {
    const t = e.target.closest(selector);
    if (!t || !root.contains(t)) return tipEl.classList.remove("show");
    const content = html(t);
    if (!content) return;
    tipEl.innerHTML = content;
    tipEl.style.left = `${Math.min(e.clientX + 14, innerWidth - tipEl.offsetWidth - 8)}px`;
    tipEl.style.top = `${e.clientY + 14}px`;
    tipEl.classList.add("show");
  });
  root.addEventListener("mouseleave", () => tipEl.classList.remove("show"));
}
