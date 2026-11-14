// Draws metrics.stats.svg and metrics.languages.svg from the GitHub API.
// Needs GH_TOKEN: a fine-grained token with read access to your repos.
// Only totals and language names are written; no repo names leave the API.
import { writeFileSync } from "node:fs";

const token = process.env.GH_TOKEN;
if (!token) throw new Error("GH_TOKEN is not set");
const outDir = process.argv[2] ?? ".";
const headers = { Authorization: `Bearer ${token}`, "User-Agent": "profile-cards" };

const IGNORED = new Set(["HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Procfile", "Batchfile", "Smarty", "Jupyter Notebook", "MDX"]);
const COLORS = {
  TypeScript: "#3178c6", JavaScript: "#f1e05a", Kotlin: "#A97BFF", Java: "#b07219", Go: "#00ADD8",
  Swift: "#F05138", Python: "#3572A5", Shell: "#89e051", Lua: "#000080", "C++": "#f34b7d", C: "#555555",
  PHP: "#4F5D95", Rust: "#dea584", Dart: "#00B4AB", Svelte: "#ff3e00", Vue: "#41b883", Astro: "#ff5a03",
  "Objective-C": "#438eff", "Objective-C++": "#6866fb", Ruby: "#701516", OCaml: "#ef7a08", Haskell: "#5e5086",
  TeX: "#3D6117", PLpgSQL: "#336790", SQL: "#e38c00", Groovy: "#4298b8", Nix: "#7e7eff",
};
const FALLBACK = ["#7aa2f7", "#bb9af7", "#9ece6a", "#e0af68", "#f7768e", "#2ac3de", "#ff9e64", "#73daca"];

const T = { bg: "#1a1b27", border: "#2a2e42", title: "#70a5fd", text: "#c0caf5", muted: "#8b93b8", accent: "#bf91f3" };
const FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif";
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const fmt = (n) => (n >= 10000 ? `${(n / 1000).toFixed(1)}k` : n.toLocaleString("en-US"));

async function gql(query) {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST", headers: { ...headers, "Content-Type": "application/json" }, body: JSON.stringify({ query }),
  });
  const body = await res.json();
  if (!res.ok || body.errors) throw new Error(`GraphQL: ${res.status} ${JSON.stringify(body.errors ?? body)}`);
  return body.data;
}

async function rest(path) {
  const res = await fetch(`https://api.github.com${path}`, { headers: { ...headers, Accept: "application/vnd.github+json" } });
  if (!res.ok) throw new Error(`GET ${path}: ${res.status} ${await res.text()}`);
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

function card(width, height, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img">
<style>
  text { font-family: ${FONT}; }
  .fade { opacity: 0; animation: fade .5s ease-out forwards; }
  @keyframes fade { to { opacity: 1; } }
  @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
  .bar { transform-origin: left; animation: grow .8s ease-out forwards; }
</style>
<rect x=".5" y=".5" rx="10" width="${width - 1}" height="${height - 1}" fill="${T.bg}" stroke="${T.border}"/>
${body}
</svg>
`;
}

function statsCard(v) {
  const c = v.contributionsCollection;
  const days = c.contributionCalendar.weeks.flatMap((w) => w.contributionDays);
  let streak = 0, best = 0;
  for (const d of days) { streak = d.contributionCount > 0 ? streak + 1 : 0; best = Math.max(best, streak); }
  const rows = [
    ["\u25c6", "Contributions (last year)", c.contributionCalendar.totalContributions],
    ["\u25cf", "Commits", c.totalCommitContributions + c.restrictedContributionsCount],
    ["\u2600", "Active days", days.filter((d) => d.contributionCount > 0).length],
    ["\u21af", "Longest streak", `${best} days`],
    ["\u21c4", "Pull requests", c.totalPullRequestContributions],
    ["\u2713", "Code reviews", c.totalPullRequestReviewContributions],
    ["\u25a3", "Repositories", v.repositories.totalCount],
  ].filter(([, label, value]) => value !== 0 || label === "Repositories").slice(0, 6);
  const body = rows.map(([icon, label, value], i) => {
    const y = 72 + i * 25;
    return `<g class="fade" style="animation-delay:${150 + i * 120}ms">
  <text x="28" y="${y}" fill="${T.accent}" font-size="13">${icon}</text>
  <text x="50" y="${y}" fill="${T.text}" font-size="14" font-weight="600">${label}</text>
  <text x="365" y="${y}" fill="${T.text}" font-size="14" font-weight="700" text-anchor="end">${typeof value === "number" ? fmt(value) : esc(value)}</text>
</g>`;
  }).join("\n");
  return card(400, 200, `<text x="25" y="38" fill="${T.title}" font-size="18" font-weight="700">${esc(v.name || v.login)}'s GitHub</text>\n${body}`);
}

function languagesCard(totals) {
  const sum = totals.reduce((a, [, b]) => a + b, 0);
  const topSum = totals.slice(0, 8).reduce((a, [, b]) => a + b, 0);
  const top = totals.slice(0, 8).map(([name, bytes], i) => ({
    name, pct: (bytes / sum) * 100, color: COLORS[name] ?? FALLBACK[i % FALLBACK.length],
  }));
  const barW = 350;
  let x = 25;
  const segs = top.map((l) => {
    const w = Math.max(((l.pct * sum) / topSum / 100) * barW, 2);
    const seg = `<rect x="${x.toFixed(1)}" y="55" width="${w.toFixed(1)}" height="10" fill="${l.color}"/>`;
    x += w;
    return seg;
  }).join("");
  const legend = top.map((l, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const lx = 25 + col * 180, ly = 95 + row * 26;
    return `<g class="fade" style="animation-delay:${300 + i * 100}ms">
  <circle cx="${lx + 5}" cy="${ly - 4}" r="5" fill="${l.color}"/>
  <text x="${lx + 16}" y="${ly}" fill="${T.text}" font-size="13">${esc(l.name)} <tspan fill="${T.muted}">${l.pct.toFixed(1)}%</tspan></text>
</g>`;
  }).join("\n");
  return card(400, 200, `<text x="25" y="38" fill="${T.title}" font-size="18" font-weight="700">Most used languages</text>
<clipPath id="bar"><rect x="25" y="55" width="${barW}" height="10" rx="5"/></clipPath>
<g clip-path="url(#bar)"><g class="bar">${segs}</g></g>
${legend}`);
}

const { viewer } = await gql(`{ viewer { login name
  repositories(ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) { totalCount }
  contributionsCollection { totalCommitContributions totalPullRequestContributions totalIssueContributions
    totalPullRequestReviewContributions restrictedContributionsCount contributionCalendar { totalContributions weeks { contributionDays { contributionCount } } } } } }`);

const repos = (await allRepos()).filter((r) => !r.fork && !r.archived && r.name !== r.owner.login);
const bytes = {};
for (const r of repos) {
  const langs = await rest(`/repos/${r.full_name}/languages`);
  for (const [name, n] of Object.entries(langs)) if (!IGNORED.has(name)) bytes[name] = (bytes[name] ?? 0) + n;
}
const totals = Object.entries(bytes).sort((a, b) => b[1] - a[1]);

writeFileSync(`${outDir}/metrics.stats.svg`, statsCard(viewer));
writeFileSync(`${outDir}/metrics.languages.svg`, languagesCard(totals));
console.log(`Wrote cards from ${repos.length} repos, ${totals.length} languages.`);
