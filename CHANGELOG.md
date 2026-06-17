# Changelog

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
