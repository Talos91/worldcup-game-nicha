# CLAUDE.md — World Cup 2026 scoreboard (Nicha vs Daniele)

Context and working notes for Claude sessions on this project.

## What this is
A fun head-to-head World Cup tracker. Each player has 4 teams; results are
scored **+3 win / +1 draw / −1 loss** per team, summed per player.
- **Nicha:** Spain, South Korea, Argentina, United States
- **Daniele:** Germany, Japan, Mexico, Colombia

## Architecture
- `update_scores.py` — zero-dependency Python. Fetches football-data.org
  competition `WC` matches, matches our teams by **team id** (stable), computes
  scores, writes `data.json`. Only rewrites when real data changes (it ignores
  its own `updatedAt`), so the cron commits only on genuine updates.
- `index.html` — static page; reads `data.json`, renders the scoreboard, and
  auto-refreshes every 5 min. The API key never reaches the browser. Sections:
  who's-winning hero + scoring-rules strip, Standings (form dots), Recent results
  + Upcoming feeds (head-to-head aware), and data-driven curiosities + trivia.
- `data.json` keys: `players` (each with `agg` totals; each team has `group`
  standing + `coach`), `groups` (ALL 12 group tables, each flagged `hasTracked`),
  `timeline` (cumulative points per player after each match — drives the lead
  chart), `recent` / `upcoming` (matches carry half-time, referee, duration,
  penalties), `scorers`, `curiosities` — all computed in the updater.
- Endpoints used (all free tier): `/competitions/WC/matches`, `/standings`,
  `/teams` (coaches only — squads discarded), `/scorers`.
- `og.png` is the link-preview image, made by `gen_og.py` (Pillow, run once
  locally — score-agnostic so it never goes stale); referenced via Open Graph
  meta tags in index.html. The page also has confetti (leader's colour on load),
  a live next-match countdown, and the lead-tracker chart — all client-side.
- Per-match goalscorers are NOT on the free plan (match `goals` array is empty),
  so the page shows tournament top scorers with tracked players highlighted.
  Head-to-head (`/matches/{id}/head2head`) IS wired in for ⚔ matches, but the
  free plan reliably returns only `numberOfMatches` + `totalGoals` (W/D/L split
  is usually 0), so the page shows meetings + goals (W/D/L only when present).
  NOT on free plan at all: venue, attendance, odds, per-match goalscorers.
- API key: env var `FOOTBALL_DATA_API_KEY`, else git-ignored `apikey.txt`.

## Automation
- **GitHub Actions** (`.github/workflows/update.yml`, cron `7 1,9,17 * * *` UTC)
  is the live updater: runs `update_scores.py` 3×/day at ~08:00 / 16:00 / 00:00
  Bangkok (ICT) and commits `data.json`, which redeploys Pages. 24/7,
  laptop-independent.
  Needs repo secret **`FOOTBALL_DATA_API_KEY`** (Settings → Secrets and variables
  → Actions).
- The Claude scheduled task `worldcup-scores-update` is now **disabled** (it only
  ran while the app was open). Don't run both at once — two crons pushing the same
  file conflict.
- Hosting: **GitHub Pages** at github.com/Talos91/worldcup-game-nicha (Deploy from
  branch, `main` / root). The local repo will fall behind the Actions commits —
  run `git pull` before any local edit/push.

## Conventions
- Never commit `apikey.txt`.
- The updater is the source of truth for scoring — don't hand-edit `data.json`.
- Keep `CHANGELOG.md` and `ROADMAP.md` current each session.

## Open decisions
- **Penalty shootouts (knockouts, ~early July):** currently scored as Win(+3) /
  Loss(−1) by the official result, NOT a draw. Confirm the rule with Nicha
  before the knockouts. To switch to draw-counts-as-even, change the
  `winner == "DRAW"` handling in `team_record()`.
