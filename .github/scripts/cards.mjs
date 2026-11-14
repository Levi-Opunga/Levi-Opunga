// Draws the stats and languages cards from the GitHub API in the livery of
// assets/hero-*.svg, in light and dark. Needs GH_TOKEN with read access to your repos.
// Only totals and language names are written; no repo names leave the API.
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const token = process.env.GH_TOKEN;
if (!token) throw new Error("GH_TOKEN is not set");
const outDir = process.argv[2] ?? ".";
const headers = { Authorization: `Bearer ${token}`, "User-Agent": "profile-cards" };

const IGNORED = new Set(["HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Procfile", "Batchfile", "Smarty", "Jupyter Notebook", "MDX"]);
const THEMES = {
  light: {
    paint: "#F3F4F6", ink: "#000000", muted: "#4B5563", bubble: "#E4E6EA", white: "#FFFFFF",
    black: "#000000", red: "#BB0000", green: "#006B3F",
    langs: ["#000000", "#BB0000", "#006B3F", "#6B7280", "#9CA3AF", "#C9CDD3"],
  },
  dark: {
    paint: "#16181C", ink: "#F5F5F5", muted: "#9CA3AF", bubble: "#2A2D33", white: "#F5F5F5",
    black: "#000000", red: "#D42222", green: "#0E8A55",
    langs: ["#F5F5F5", "#D42222", "#0E8A55", "#9CA3AF", "#6B7280", "#474B53"],
  },
};
const DISPLAY = readFileSync(new URL("./display-subset.woff.b64", import.meta.url), "utf8").trim();
const SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const num = (n) => n.toLocaleString("en-US");

async function gql(query) {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ query }),
  });
  const body = await res.json();
  if (!res.ok || body.errors) throw new Error(`GitHub GraphQL request failed: ${res.status}`);
  return body.data;
}

async function rest(path) {
  const res = await fetch(`https://api.github.com${path}`, { headers: { ...headers, Accept: "application/vnd.github+json" } });
  if (!res.ok) throw new Error(`GitHub API request failed: ${res.status}`);
  return res.json();
}

async function allRepos() {
  const repos = [];
  for (let page = 1; ; page++) {
    const batch = await rest(`/user/repos?affiliation=owner,collaborator,organization_member&per_page=100&page=${page}`);
    repos.push(...batch);
    if (batch.length < 100) return repos;
  }
}

// Shared frame: painted panel with small flag stripes in the top-right corner.
function panel(t, width, height, body) {
  const bands = [[t.black, 12], [t.white, 3], [t.red, 12], [t.white, 3], [t.green, 12]];
  let x = width - 70;
  const stripes = bands.map(([c, w]) => {
    const p = `<polygon points="${x},${height} ${x + w},${height} ${x + w + 150},0 ${x + 150},0" fill="${c}"/>`;
    x += w;
    return p;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img">
<defs>
  <style>
    @font-face { font-family: "Big Shoulders"; src: url(data:font/woff;base64,${DISPLAY}) format("woff"); }
    .display { font-family: "Big Shoulders", "Arial Narrow", Impact, sans-serif; font-weight: 900; }
    .sans { font-family: ${SANS}; }
  </style>
  <clipPath id="frame"><rect width="${width}" height="${height}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="${width}" height="${height}" fill="${t.paint}"/>
  ${stripes}
</g>
${body}
</svg>
`;
}

function wrap(text, max) {
  const lines = [];
  let line = "";
  for (const word of text.split(" ")) {
    if ((line + " " + word).trim().length > max) { lines.push(line); line = word; }
    else line = (line + " " + word).trim();
  }
  return [...lines, line];
}

function summarize(v) {
  const c = v.contributionsCollection;
  const days = c.contributionCalendar.weeks.flatMap((w) => w.contributionDays);
  let streak = 0, best = 0;
  for (const d of days) { streak = d.contributionCount > 0 ? streak + 1 : 0; best = Math.max(best, streak); }
  return {
    name: (v.name || v.login).toUpperCase(),
    total: c.contributionCalendar.totalContributions,
    active: days.filter((d) => d.contributionCount > 0).length,
    best,
    repos: v.repositories.totalCount,
  };
}

// Stats as a mobile-money style "Confirmed." text message.
function statsCard(t, s, now) {
  const date = now.toISOString().slice(0, 10);
  const code = createHash("sha256").update(date).digest("hex").toUpperCase().slice(0, 10);
  const [yy, mm, dd] = [date.slice(2, 4), date.slice(5, 7), date.slice(8, 10)];
  const message = `${code} Confirmed. You have received ${num(s.total)} contributions from ${s.name} ` +
    `in the last 12 months. Active on ${s.active} days, longest streak ${s.best} days. ` +
    `Repositories: ${num(s.repos)}. Transaction cost, Ksh0.00.`;
  const lines = wrap(message, 44);
  const W = 420, lineH = 21, bubbleH = 26 + lines.length * lineH;
  const H = Math.max(276, 100 + bubbleH + 40);
  const text = lines.map((l, i) => `<tspan x="40" y="${121 + i * lineH}">${esc(l)}</tspan>`).join("");
  return panel(t, W, H, `
<circle cx="44" cy="48" r="20" fill="${t.ink}"/>
<text class="display" x="44" y="56" font-size="20" fill="${t.paint}" text-anchor="middle">GH</text>
<text class="sans" x="76" y="45" font-size="16" font-weight="700" fill="${t.ink}">GitHub</text>
<text class="sans" x="76" y="64" font-size="12.5" fill="${t.muted}">${dd}/${mm}/${yy}, 3:00 AM</text>
<rect x="24" y="96" width="${W - 92}" height="${bubbleH}" rx="18" fill="${t.bubble}"/>
<text class="sans" font-size="14.5" fill="${t.ink}">${text}</text>`);
}

// Languages as one slanted stripe per language, width by share.
function languagesCard(t, totals) {
  const sum = totals.reduce((a, [, b]) => a + b, 0);
  const top = totals.slice(0, 6);
  const topSum = top.reduce((a, [, b]) => a + b, 0);
  const W = 420, H = 276, barX = 24, barW = W - 140, barY = 82, barH = 40, slant = 12;
  let x = barX;
  const bands = top.map(([name, bytes], i) => {
    const w = Math.max((bytes / topSum) * barW, 8);
    const color = t.langs[i];
    const p = `<polygon points="${x + slant},${barY} ${x + w + slant},${barY} ${x + w},${barY + barH} ${x},${barY + barH}" fill="${color}" stroke="${t.paint}" stroke-width="3"/>`;
    x += w;
    return { name, pct: (bytes / sum) * 100, color, p };
  });
  const legend = bands.map((b, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const lx = 26 + col * 174, ly = 164 + row * 34;
    return `<polygon points="${lx + 5},${ly - 12} ${lx + 18},${ly - 12} ${lx + 13},${ly + 1} ${lx},${ly + 1}" fill="${b.color}" stroke="${t.muted}" stroke-width="${b.color === t.paint ? 1 : 0}"/>
<text class="sans" x="${lx + 26}" y="${ly}" font-size="14" font-weight="600" fill="${t.ink}">${esc(b.name)}</text>
<text class="sans" x="${lx + 160}" y="${ly}" font-size="13.5" fill="${t.muted}" text-anchor="end" style="font-variant-numeric: tabular-nums">${b.pct.toFixed(1)}%</text>`;
  }).join("\n");
  return panel(t, W, H, `
<text class="display" x="24" y="56" font-size="34" fill="${t.ink}">LANGUAGES</text>
<g>${bands.map((b) => b.p).join("")}</g>
${legend}`);
}

const { viewer } = await gql(`{ viewer { login name
  repositories(ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) { totalCount }
  contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount } } } } } }`);

const repos = (await allRepos()).filter((r) => !r.fork && !r.archived && r.name !== r.owner.login);
const bytes = {};
let skipped = 0;
for (const r of repos) {
  // Some orgs refuse this token; skip them without printing names (Action logs are public).
  const langs = await rest(`/repos/${r.full_name}/languages`).catch(() => (skipped++, {}));
  for (const [name, n] of Object.entries(langs)) if (!IGNORED.has(name)) bytes[name] = (bytes[name] ?? 0) + n;
}
const totals = Object.entries(bytes).sort((a, b) => b[1] - a[1]);
const summary = summarize(viewer);
const now = new Date();

for (const [mode, t] of Object.entries(THEMES)) {
  const suffix = mode === "light" ? "" : "-dark";
  writeFileSync(`${outDir}/metrics.stats${suffix}.svg`, statsCard(t, summary, now));
  writeFileSync(`${outDir}/metrics.languages${suffix}.svg`, languagesCard(t, totals));
}
console.log(`Wrote cards from ${repos.length - skipped} repos (${skipped} not readable), ${totals.length} languages.`);
