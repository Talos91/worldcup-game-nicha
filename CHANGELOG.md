# Changelog

## 2026-06-17
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
