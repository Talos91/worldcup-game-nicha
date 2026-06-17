# Changelog

## 2026-06-17 — quick stats, Golden Boot, expandable results
- Added a **head-to-head quick-stats** panel under the hero (played, wins, draws,
  losses, goals for / against), a tug-of-war bar, and a playful status line.
- Added a **Golden Boot race** section (tournament top scorers) with Nicha's and
  Daniele's players highlighted. NOTE: per-match goalscorers aren't available on
  the free football-data plan (match `goals` array is empty), so this top-scorers
  view is the closest available.
- **Recent results** and **Upcoming** now show 7 by default with a "Show all"
  toggle for the full list.
- Updater emits per-player `agg` stats and a `scorers` list.

## 2026-06-17 — 24/7 updates via GitHub Actions
- Added `.github/workflows/update.yml`: runs the updater on GitHub's servers
  ~every 30 min (cron `13,43 * * * *`) and commits data.json, so the site keeps
  updating even when the laptop is off. Requires repo secret `FOOTBALL_DATA_API_KEY`.
- Disabled the Claude scheduled task `worldcup-scores-update` so two crons don't
  push the same file. (Re-enable only if you remove the Action.)

## 2026-06-17 — richer scoreboard
- Added a scoring-rules strip up top (Win +3 / Draw +1 / Loss −1).
- New **Standings** section: compact team cards with recent-form dots.
- New **Recent results** and **Upcoming matches** feeds — consolidated across all
  8 teams, newest/soonest first, color-coded by owner, with a ⚔ flag for your
  team-vs-team clashes (e.g. South Korea vs Mexico, 19 Jun).
- New **World Cup curiosities** section: live stats (goals, goals/game, biggest
  win, wildest game, draws, your teams' goals, top team) + rotating classic
  World Cup trivia.
- Updater now also emits `recent`, `upcoming`, and `curiosities` in data.json.

## 2026-06-17 — initial build
- Initial build: static scoreboard (`index.html`), zero-dependency updater
  (`update_scores.py`), generated `data.json`. Scoring +3 / +1 / −1 per team.
- Teams matched by football-data team id; real country crests shown.
- API key moved to git-ignored `apikey.txt` (repo is safe to make public).
- Updater skips rewrites when only the timestamp would change, so the cron
  publishes only on genuine result/fixture updates.
- Created Claude scheduled task `worldcup-scores-update` (every 30 min, while
  the app is open).
- Standing at build time: **Nicha 10 – Daniele 7**.
- Pending: GitHub repo + Pages go-live (manual), and the penalty-shootout rule.
