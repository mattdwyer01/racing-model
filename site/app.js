// Racing Model dashboard: reads data/index.json, data/day/<date>.json, data/tracking.json (tools/dashboard_export.py)
const TZ = "Australia/Melbourne";
const OTHER = ["distance / going", "prep", "comments", "ground loss (past runs)", "age / sex / weight", "form shape",
  "position value"];
const state = { index: null, day: null, race: null, cache: {} };
const $ = (id) => document.getElementById(id);
const tip = $("tip");

const fmt = {
  price: (v) => (v == null ? "" : "$" + (v >= 100 ? v.toFixed(0) : v.toFixed(2))),
  pct: (v) => (v == null ? "" : Math.round(v * 100) + "%"),
  num: (v, d = 1) => (v == null ? "" : v.toFixed(d)),
  signed: (v, d = 1) => (v == null ? "" : (v > 0 ? "+" : "") + v.toFixed(d)),
  time: (iso) => (iso ? new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z")
    .toLocaleTimeString("en-AU", { timeZone: TZ, hour: "numeric", minute: "2-digit" }) : ""),
  day: (d) => new Date(d + "T00:00:00").toLocaleDateString("en-AU", { weekday: "short", day: "numeric", month: "short" }),
};
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const cls = (v) => (v == null ? "" : v > 0 ? "pos" : v < 0 ? "neg" : "");

async function getJSON(path) {
  if (!state.cache[path]) {
    const r = await fetch(path, { cache: "no-cache" });
    if (!r.ok) throw new Error(path + " " + r.status);
    state.cache[path] = await r.json();
  }
  return state.cache[path];
}

function showTip(ev, html) {
  tip.innerHTML = html; tip.hidden = false;
  const x = Math.min(ev.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
  tip.style.left = x + "px"; tip.style.top = ev.clientY + 14 + "px";
}
function hideTip() { tip.hidden = true; }

// ------------------------------------------------------------------ navigation
function renderTabs() {
  const nav = $("dayTabs"); nav.innerHTML = "";
  const days = state.index.days;
  const up = days.filter((d) => d.kind === "upcoming"), rec = days.filter((d) => d.kind === "recent").reverse();
  const add = (label, key) => {
    const b = document.createElement("button");
    b.textContent = label; b.setAttribute("role", "tab");
    b.setAttribute("aria-selected", String(state.day === key));
    b.onclick = () => selectDay(key);
    nav.appendChild(b);
  };
  up.forEach((d) => add(d.date === state.index.today ? "Today" : fmt.day(d.date), d.date));
  if (rec.length) { const s = document.createElement("span"); s.className = "sep"; s.textContent = "|"; nav.appendChild(s); }
  rec.forEach((d) => add(fmt.day(d.date), d.date));
  add("Tracking", "tracking");
}

async function selectDay(key) {
  state.day = key; renderTabs();
  if (key === "tracking") return renderTracking();
  const day = await getJSON(`data/day/${key}.json`);
  const list = $("meetings"); list.innerHTML = "";
  if (!day.meetings.length) { $("race").innerHTML = '<p class="empty">No VIC/SA/QLD races.</p>'; return; }
  let first = null;
  const now = Date.now();
  day.meetings.forEach((m) => {
    const box = document.createElement("div"); box.className = "meeting";
    box.innerHTML = `<div class="name">${esc(m.track)} <small>${esc(m.state || "")}</small></div><div class="races"></div>`;
    m.races.forEach((r) => {
      const b = document.createElement("button");
      b.className = "meet-race" + (r.resulted ? " done" : "");
      b.textContent = r.race_no ? "R" + r.race_no : "Race";
      b.title = `${r.distance}m ${r.class || ""}${r.start_utc ? " " + fmt.time(r.start_utc) : ""}`;
      b.onclick = () => selectRace(r, b);
      box.querySelector(".races").appendChild(b);
      const t = r.start_utc ? Date.parse(r.start_utc + (r.start_utc.includes("+") ? "" : "Z")) : null;
      if (!first || (t && t > now && (!first.t || first.t < now || t < first.t))) first = { r, b, t };
    });
    list.appendChild(box);
  });
  selectRace(first.r, first.b);
}

function selectRace(r, btn) {
  document.querySelectorAll(".meet-race").forEach((b) => b.setAttribute("aria-selected", String(b === btn)));
  state.race = r; renderRace(r);
}

// ------------------------------------------------------------------ race view
function paceBar(p) {
  if (p.slow == null) return "";
  const seg = [["slow", p.slow, "var(--seq-250)"], ["even", p.even, "var(--seq-450)"], ["fast", p.fast, "var(--seq-650)"]];
  return `<div class="row"><div class="pace" aria-hidden="true">${seg.map(([n, v, c]) =>
    `<span style="width:${(v * 100).toFixed(1)}%;background:${c}" title="${n} ${fmt.pct(v)}"></span>`).join("")}</div>
    <div class="legend">${seg.map(([n, v, c]) => `<span><i style="background:${c}"></i>${n} ${fmt.pct(v)}</span>`).join("")}</div></div>`;
}

function speedMap(r) {
  const run = [...r.runners].sort((a, b) => (a.settle ?? 1) - (b.settle ?? 1));
  const rowH = 24, left = 190, right = 70, top = 22, w = 760, h = top + rowH * run.length + 8;
  const x = (s) => left + (w - left - right) * (s ?? 0.5);
  let svg = `<svg class="map" viewBox="0 0 ${w} ${h}" role="img" aria-label="Speed map: projected settling position">`;
  svg += `<g class="axis"><text x="${left}" y="13">Leader</text><text x="${w - right}" y="13" text-anchor="end">Back</text>
    <text x="${w - 4}" y="13" text-anchor="end">P(leads)</text></g>`;
  [0, 0.25, 0.5, 0.75, 1].forEach((t) => { svg += `<line class="grid" x1="${x(t)}" x2="${x(t)}" y1="${top - 4}" y2="${h - 6}"/>`; });
  run.forEach((d, i) => {
    const y = top + rowH * i + rowH / 2;
    svg += `<g class="m" data-i="${i}"><rect x="0" y="${y - rowH / 2}" width="${w}" height="${rowH}" fill="transparent"/>
      <text x="4" y="${y + 4}">${esc(d.horse)} <tspan fill="var(--text-muted)">(${d.barrier ?? "-"})</tspan></text>
      <circle cx="${x(d.settle)}" cy="${y}" r="7" fill="var(--series-1)"/>
      <text x="${w - 4}" y="${y + 4}" text-anchor="end">${fmt.pct(d.p_lead)}</text></g>`;
  });
  svg += "</svg>";
  const wrap = document.createElement("div"); wrap.innerHTML = svg;
  wrap.querySelectorAll("g.m").forEach((g) => {
    const d = run[+g.dataset.i];
    g.addEventListener("mousemove", (ev) => showTip(ev, `<b>${esc(d.horse)}</b> barrier ${d.barrier ?? "-"}<br>
      settle ${fmt.num(d.settle, 2)} (rank ${d.settle_rank})<br>leads ${fmt.pct(d.p_lead)}<br>
      extra ground ${fmt.signed(d.extra_ground)} m<br>race-day ${fmt.signed(d.raceday_adj)} WPR`));
    g.addEventListener("mouseleave", hideTip);
  });
  return wrap;
}

function ratingsTable(r) {
  const res = r.resulted;
  const head = ["Horse", "Jockey", "Rating", "vs field", "Ability", "Race-day", "J/T", "Other", "Model", "Blend", "Fixed",
    "Edge"].concat(res ? ["Fin", "SP", "WPR", "vs proj"] : []);
  const rows = r.runners.map((x, i) => {
    const g = x.groups || {};
    const other = OTHER.reduce((s, k) => s + (g[k] || 0), 0);
    const rd = (g["race-day projection"] || 0) + (g["track bias"] || 0);
    const edge = x.edge_fixed;
    const edgeCell = edge == null ? "" : edge > 0 ? `<span class="edge-badge">&#9650; ${fmt.pct(edge)}</span>` :
      `<span class="muted">${fmt.pct(edge)}</span>`;
    const rr = x.result || {};
    const tail = res ? [`<b>${rr.finish ?? "-"}</b>`, fmt.price(rr.sp), fmt.num(rr.wpr),
      `<span class="${cls(rr.wpr != null && x.rating != null ? rr.wpr - x.rating : null)}">${
        rr.wpr != null && x.rating != null ? fmt.signed(rr.wpr - x.rating) : ""}</span>`] : [];
    return `<tr><td class="l">${i + 1}. ${esc(x.horse)} <span class="muted">(${x.barrier ?? "-"})</span></td>
      <td class="l">${esc(x.jockey || "")}</td><td><b>${fmt.num(x.rating)}</b></td>
      <td class="${cls(x.vs_field)}">${fmt.signed(x.vs_field)}</td><td>${fmt.signed(g.ability)}</td>
      <td>${fmt.signed(rd)}</td><td>${fmt.signed(g["jockey / trainer"])}</td><td>${fmt.signed(other)}</td>
      <td>${fmt.price(x.model_price)}</td><td>${fmt.price(x.blend_price)}</td><td>${fmt.price(x.fixed)}</td>
      <td>${edgeCell}</td>${tail.map((t) => `<td>${t}</td>`).join("")}</tr>`;
  });
  return `<div class="table-wrap"><table><thead><tr>${head.map((h, i) => `<th class="${i < 2 ? "l" : ""}">${h}</th>`)
    .join("")}</tr></thead><tbody>${rows.join("")}</tbody></table></div>`;
}

function renderRace(r) {
  const el = $("race");
  const res = r.resulted;
  const top = r.runners[0];
  const winner = res ? r.runners.find((x) => x.result && x.result.finish === 1) : null;
  el.innerHTML = `<h2>${esc(r.track)} ${r.race_no ? "R" + r.race_no : ""}</h2>
    <div class="row sub"><span>${r.distance}m</span><span>${esc(r.class || "")}</span><span>${esc(r.going || "")}</span>
      ${r.rail ? `<span>Rail ${esc(r.rail)}</span>` : ""}${r.start_utc ? `<span>${fmt.time(r.start_utc)}</span>` : ""}
      <span class="pill">${res ? "Result" : "Upcoming"}</span></div>
    ${res && winner ? `<p class="sub">Winner <b>${esc(winner.horse)}</b> (rated #${r.runners.indexOf(winner) + 1},
      blend ${fmt.price(winner.blend_price)}, SP ${fmt.price(winner.result.sp)}). Top rated ${esc(top.horse)} finished
      ${top.result?.finish ?? "-"}.</p>` : ""}
    <h3>Pace</h3><p class="sub">Projected ${fmt.signed(r.pace.vs_avg)} vs the average for the distance${
      res && r.pace.actual_shape_early != null ? `; actual early shape ${fmt.signed(r.pace.actual_shape_early)}` : ""}</p>
    ${paceBar(r.pace)}
    <h3>Speed map</h3><div id="map"></div>
    <h3>Ratings and prices</h3>
    <p class="sub">Rating = projected WPR; contributions in WPR points vs the field. Model and blend prices are fair
      (no margin). Edge = blend probability x fixed price - 1.</p>
    ${ratingsTable(r)}`;
  $("map").appendChild(speedMap(r));
}

// ------------------------------------------------------------------ tracking view
async function renderTracking() {
  $("meetings").innerHTML = "";
  const t = await getJSON("data/tracking.json");
  const el = $("race");
  if (!t.days || !t.days.length) { el.innerHTML = '<p class="empty">No resulted races tracked yet.</p>'; return; }
  const T = t.total;
  const diff = T.ll_blend - T.ll_sp;
  el.innerHTML = `<h2>Model tracking</h2>
    <p class="sub">Projections archived before each race, scored against the result. Log loss per race: lower is better.</p>
    <div class="tiles">
      <div class="tile"><div class="v">${T.races}</div><div class="k">resulted races</div></div>
      <div class="tile"><div class="v ${diff < 0 ? "pos" : "neg"}">${fmt.signed(diff, 4)}</div><div class="k">blend minus SP log loss</div></div>
      <div class="tile"><div class="v">${fmt.num(T.ll_model, 3)}</div><div class="k">model alone log loss</div></div>
      <div class="tile"><div class="v">${fmt.pct(T.top_rated_won)}</div><div class="k">top rated won</div></div>
    </div>
    <h3>Blend minus SP, cumulative average by day</h3><div id="chart"></div>
    <h3>By day</h3><div class="table-wrap"><table><thead><tr><th class="l">Date</th><th>Races</th><th>Model</th>
      <th>Blend</th><th>SP</th><th>Blend - SP</th><th>Top rated won</th></tr></thead><tbody>
      ${t.days.slice().reverse().map((d) => `<tr><td class="l">${fmt.day(d.date)}</td><td>${d.races}</td>
        <td>${fmt.num(d.ll_model, 3)}</td><td>${fmt.num(d.ll_blend, 3)}</td><td>${fmt.num(d.ll_sp, 3)}</td>
        <td class="${cls(-(d.ll_blend - d.ll_sp))}">${fmt.signed(d.ll_blend - d.ll_sp, 4)}</td>
        <td>${fmt.pct(d.top_rated_won)}</td></tr>`).join("")}</tbody></table></div>`;
  // cumulative race-weighted mean of blend - SP
  let n = 0, s = 0;
  const pts = t.days.map((d) => { n += d.races; s += (d.ll_blend - d.ll_sp) * d.races; return { date: d.date, v: s / n }; });
  const w = 760, h = 200, l = 60, rgt = 16, tp = 12, b = 26;
  const vs = pts.map((p) => p.v).concat([0]);
  const lo = Math.min(...vs), hi = Math.max(...vs), pad = (hi - lo || 0.01) * 0.15;
  const y = (v) => tp + (h - tp - b) * (1 - (v - (lo - pad)) / (hi - lo + 2 * pad));
  const x = (i) => l + (w - l - rgt) * (pts.length === 1 ? 0.5 : i / (pts.length - 1));
  let svg = `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Cumulative blend minus SP log loss">`;
  [lo - pad, 0, hi + pad].forEach((v) => { svg += `<line class="grid" x1="${l}" x2="${w - rgt}" y1="${y(v)}" y2="${y(v)}"/>
    <text x="${l - 6}" y="${y(v) + 4}" text-anchor="end">${fmt.signed(v, 4)}</text>`; });
  svg += `<polyline fill="none" stroke="var(--series-1)" stroke-width="2" points="${pts.map((p, i) => `${x(i)},${y(p.v)}`).join(" ")}"/>`;
  pts.forEach((p, i) => { svg += `<circle cx="${x(i)}" cy="${y(p.v)}" r="4" fill="var(--series-1)" data-i="${i}"/>
    <rect x="${x(i) - 12}" y="${tp}" width="24" height="${h - tp - b}" fill="transparent" data-i="${i}"/>`; });
  [0, pts.length - 1].forEach((i) => { svg += `<text x="${x(i)}" y="${h - 8}" text-anchor="middle">${fmt.day(pts[i].date)}</text>`; });
  svg += "</svg>";
  const c = $("chart"); c.innerHTML = svg;
  c.querySelectorAll("rect[data-i]").forEach((m) => {
    const p = pts[+m.dataset.i];
    m.addEventListener("mousemove", (ev) => showTip(ev, `${fmt.day(p.date)}<br>blend - SP to date ${fmt.signed(p.v, 4)}`));
    m.addEventListener("mouseleave", hideTip);
  });
}

// ------------------------------------------------------------------ boot
(async function boot() {
  try {
    state.index = await getJSON("data/index.json");
  } catch (e) {
    $("race").innerHTML = '<p class="empty">No data yet: run tools/dashboard_export.py.</p>'; $("meta").textContent = ""; return;
  }
  const gen = new Date(state.index.generated_utc + "Z").toLocaleString("en-AU", { timeZone: TZ });
  $("meta").textContent = `updated ${gen} | model trained to ${state.index.model.train_end}`;
  const up = state.index.days.find((d) => d.kind === "upcoming") || state.index.days[state.index.days.length - 1];
  selectDay(up ? up.date : "tracking");
})();
