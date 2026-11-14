// Draws metrics.stats.svg and metrics.languages.svg from the GitHub API, in the
// matatu livery of assets/hero.svg. Needs GH_TOKEN with read access to your repos.
// Only totals and language names are written; no repo names leave the API.
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

const token = process.env.GH_TOKEN;
if (!token) throw new Error("GH_TOKEN is not set");
const outDir = process.argv[2] ?? ".";
const headers = { Authorization: `Bearer ${token}`, "User-Agent": "profile-cards" };

const IGNORED = new Set(["HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Procfile", "Batchfile", "Smarty", "Jupyter Notebook", "MDX"]);
const C = {
  indigo: "#1B1446", deep: "#110C30", yellow: "#FFD23F", pink: "#FF3E8A", cyan: "#2EC4E6",
  amber: "#FFB000", chrome: "#F4F6FF", violet: "#9B7BFF", mint: "#5EE6A8", muted: "#A9A3D6",
};
const STRIPES = [C.pink, C.yellow, C.cyan, C.chrome, C.amber, C.violet, C.mint, "#FF8A5C"];
const BUNGEE = readFileSync(new URL("./bungee-subset.woff.b64", import.meta.url), "utf8").trim();
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

// Shared frame: indigo panel, chrome trim top and bottom, racing stripes in one corner.
function panel(width, height, body, { stripes = true } = {}) {
  const s = (off, w, color) =>
    `<polygon points="${width - 150 + off},0 ${width - 150 + off + w},0 ${width - 230 + off + w},${height} ${width - 230 + off},${height}" fill="${color}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img">
<defs>
  <style>
    @font-face { font-family: Bungee; src: url(data:font/woff;base64,${BUNGEE}) format("woff"); }
    .sign { font-family: Bungee, Impact, sans-serif; }
    .sans { font-family: ${SANS}; }
  </style>
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2A1F6E"/><stop offset=".55" stop-color="${C.indigo}"/><stop offset="1" stop-color="${C.deep}"/>
  </linearGradient>
  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#B9BED6"/>
    <stop offset=".5" stop-color="#6E7391"/><stop offset="1" stop-color="#E3E6F5"/>
  </linearGradient>
  <clipPath id="frame"><rect width="${width}" height="${height}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="${width}" height="${height}" fill="url(#panel)"/>
  ${stripes ? `<g opacity=".9">${s(0, 34, C.pink)}${s(44, 14, C.yellow)}${s(66, 6, C.cyan)}</g>` : ""}
  <rect width="${width}" height="7" fill="url(#chrome)"/>
  <rect y="${height - 7}" width="${width}" height="7" fill="url(#chrome)"/>
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

// Stats as a mobile-money style "Confirmed." SMS.
function statsCard(v, now) {
  const c = v.contributionsCollection;
  const days = c.contributionCalendar.weeks.flatMap((w) => w.contributionDays);
  let streak = 0, best = 0;
  for (const d of days) { streak = d.contributionCount > 0 ? streak + 1 : 0; best = Math.max(best, streak); }
  const active = days.filter((d) => d.contributionCount > 0).length;
  const total = c.contributionCalendar.totalContributions;

  const date = now.toISOString().slice(0, 10);
  const code = createHash("sha256").update(date).digest("hex").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 10);
  const [yy, mm, dd] = [date.slice(2, 4), date.slice(5, 7), date.slice(8, 10)];
  const message = `${code} Confirmed. You have received ${num(total)} contributions from ` +
    `${(v.name || v.login).toUpperCase()} in the last 12 months. Active on ${active} days, ` +
    `longest streak ${best} days. Repositories: ${num(v.repositories.totalCount)}. Transaction cost, Ksh0.00.`;

  const lines = wrap(message, 44);
  const W = 420, lineH = 21, bubbleH = 28 + lines.length * lineH;
  const H = Math.max(276, 96 + bubbleH + 44);
  const text = lines.map((l, i) => `<tspan x="40" y="${118 + i * lineH}">${esc(l)}</tspan>`).join("");
  return panel(W, H, `
<circle cx="44" cy="46" r="20" fill="${C.yellow}"/>
<text class="sign" x="44" y="53" font-size="17" fill="${C.deep}" text-anchor="middle">GH</text>
<text class="sign" x="76" y="44" font-size="17" fill="${C.chrome}">GITHUB</text>
<text class="sans" x="76" y="63" font-size="12.5" fill="${C.muted}">${dd}/${mm}/${yy}, 3:00 AM</text>
<path d="M22 ${92 + bubbleH} q2 -10 2 -18 V108 a16 16 0 0 1 16 -16 h${W - 104} a16 16 0 0 1 16 16 v${bubbleH - 32} a16 16 0 0 1 -16 16 h-${W - 110} q-8 6 -18 2 z" fill="${C.chrome}"/>
<text class="sans" font-size="14.5" fill="${C.deep}">${text}</text>
<text class="sans" x="40" y="${H - 24}" font-size="12" fill="${C.muted}">Delivered</text>`);
}

// Languages as livery paint stripes: one slanted band per language, width by share.
function languagesCard(totals) {
  const sum = totals.reduce((a, [, b]) => a + b, 0);
  const top = totals.slice(0, 6);
  const topSum = top.reduce((a, [, b]) => a + b, 0);
  const W = 420, H = 276, barX = 24, barW = W - 48, barY = 74, barH = 44, slant = 14;
  let x = barX;
  const bands = top.map(([name, bytes], i) => {
    const w = Math.max((bytes / topSum) * barW, 10);
    const color = STRIPES[i];
    const p = `<polygon points="${x + slant},${barY} ${x + w + slant},${barY} ${x + w},${barY + barH} ${x},${barY + barH}" fill="${color}" stroke="${C.deep}" stroke-width="3"/>`;
    x += w;
    return { name, pct: (bytes / sum) * 100, color, p };
  });
  const legend = bands.map((b, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const lx = 28 + col * 196, ly = 156 + row * 38;
    return `<polygon points="${lx + 6},${ly - 13} ${lx + 22},${ly - 13} ${lx + 16},${ly + 1} ${lx},${ly + 1}" fill="${b.color}"/>
<text class="sans" x="${lx + 32}" y="${ly}" font-size="15" font-weight="600" fill="${C.chrome}">${esc(b.name)}</text>
<text class="sans" x="${lx + 176}" y="${ly}" font-size="14" fill="${C.muted}" text-anchor="end">${b.pct.toFixed(1)}%</text>`;
  }).join("\n");
  return panel(W, H, `
<text class="sign" x="24" y="50" font-size="24" fill="${C.yellow}" stroke="${C.deep}" stroke-width="1">Languages</text>
<g>${bands.map((b) => b.p).join("")}</g>
${legend}`, { stripes: false });
}

const { viewer } = await gql(`{ viewer { login name
  repositories(ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) { totalCount }
  contributionsCollection { totalCommitContributions restrictedContributionsCount
    contributionCalendar { totalContributions weeks { contributionDays { contributionCount } } } } } }`);

const repos = (await allRepos()).filter((r) => !r.fork && !r.archived && r.name !== r.owner.login);
const bytes = {};
let skipped = 0;
for (const r of repos) {
  // Some orgs refuse this token; skip them without printing names (Action logs are public).
  const langs = await rest(`/repos/${r.full_name}/languages`).catch(() => (skipped++, {}));
  for (const [name, n] of Object.entries(langs)) if (!IGNORED.has(name)) bytes[name] = (bytes[name] ?? 0) + n;
}
const totals = Object.entries(bytes).sort((a, b) => b[1] - a[1]);

writeFileSync(`${outDir}/metrics.stats.svg`, statsCard(viewer, new Date()));
writeFileSync(`${outDir}/metrics.languages.svg`, languagesCard(totals));
console.log(`Wrote cards from ${repos.length - skipped} repos (${skipped} not readable), ${totals.length} languages.`);
