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
  auto-refreshes every 5 min. The API key never reaches the browser.
- API key: env var `FOOTBALL_DATA_API_KEY`, else git-ignored `apikey.txt`.

## Automation
- Claude scheduled task **`worldcup-scores-update`**, cron `7,37 * * * *`
  (every 30 min). Runs the updater, then pushes `data.json`. Runs **only while
  the Claude app is open** (catches up on next launch).
- Hosting: **GitHub Pages** (public repo). No `gh` CLI on this machine — repo
  create / first push / Pages-enable are manual browser steps.

## Conventions
- Never commit `apikey.txt`.
- The updater is the source of truth for scoring — don't hand-edit `data.json`.
- Keep `CHANGELOG.md` and `ROADMAP.md` current each session.

## Open decisions
- **Penalty shootouts (knockouts, ~early July):** currently scored as Win(+3) /
  Loss(−1) by the official result, NOT a draw. Confirm the rule with Nicha
  before the knockouts. To switch to draw-counts-as-even, change the
  `winner == "DRAW"` handling in `team_record()`.
