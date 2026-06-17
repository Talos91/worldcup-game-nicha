# World Cup 2026 — Nicha vs Daniele 🏆

A tiny auto-updating scoreboard for our World Cup game. Each of us picked 4
teams; their results are scored automatically.

**Scoring (per team):** win = **+3**, draw = **+1**, loss = **−1**.

| Nicha | Daniele |
|-------|---------|
| 🇪🇸 Spain | 🇩🇪 Germany (UEFA) |
| 🇰🇷 South Korea | 🇯🇵 Japan (AFC) |
| 🇦🇷 Argentina | 🇲🇽 Mexico (CONCACAF) |
| 🇺🇸 United States | 🇨🇴 Colombia (CONMEBOL) |

## How it works

- **`update_scores.py`** fetches the latest FIFA World Cup results from
  [football-data.org](https://www.football-data.org), computes each player's
  total, and writes **`data.json`**. Pure Python standard library — no installs.
- **`index.html`** is the page. It reads `data.json`, renders the scoreboard,
  and auto-refreshes every 5 minutes. No backend; the API key never touches the
  browser.
- A **Claude scheduled task** runs `update_scores.py` every 30 minutes and
  pushes the new `data.json` here, so GitHub Pages republishes automatically.

> ⚠️ The scheduled task runs while the Claude app is open (it catches up on the
> next launch if it was closed). For true 24/7 updates even with the app closed,
> see "GitHub Actions" below.

## Update it by hand

```powershell
cd C:\Users\itisf\worldcup-game
python update_scores.py
git add data.json; git commit -m "update scores"; git push
```

## API key

The football-data.org key is read from the `FOOTBALL_DATA_API_KEY` environment
variable, or from **`apikey.txt`** next to the script. `apikey.txt` is
git-ignored, so the key is never committed — this repo is safe to make public.

## Knockout rounds (worth agreeing before July)

In the group stage every match is a clean win/draw/loss. In the knockouts there
are no draws — a match decided on penalties is currently recorded as a
**win (+3)** for the shootout winner and a **loss (−1)** for the loser (the
official FIFA result). If you'd rather count a penalty result as a draw
(+1 each), it's a one-line change.

## Optional: 24/7 updates with GitHub Actions

If you want updates even when the Claude app is closed, a GitHub Actions
workflow can run the updater on GitHub's own cron (free) with the API key stored
as a repo secret. Ask and it can be added.

## Files

- `index.html` — the scoreboard page
- `update_scores.py` — the updater
- `data.json` — generated standings (committed so the page loads instantly)
- `apikey.txt` — your API key (git-ignored, local only)
