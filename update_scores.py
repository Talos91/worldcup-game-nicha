#!/usr/bin/env python3
"""Update World Cup game scores for Nicha vs Daniele.

Fetches FIFA World Cup matches from football-data.org, computes the head-to-head
game score and writes data.json next to this script for the static page to read.

Game rules: win = +3, draw = +1, loss = -1 (per team, summed per player).

Pure Python standard library -- no `pip install` needed. Runs anywhere Python 3
runs (local, GitHub Actions, a Claude scheduled task, etc.).

The API key is read from the FOOTBALL_DATA_API_KEY environment variable, falling
back to the personal key below so it "just works" locally. If you push this to a
PUBLIC repo, set the key as a secret/env var and delete the fallback string.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

COMPETITION = "WC"
API_URL = f"https://api.football-data.org/v4/competitions/{COMPETITION}/matches"


def load_api_key():
    """Key comes from the FOOTBALL_DATA_API_KEY env var, else apikey.txt next to
    this script (git-ignored). Never hard-coded -- safe to push to a public repo."""
    key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if key and key.strip():
        return key.strip()
    here = os.path.dirname(os.path.abspath(__file__))
    keyfile = os.path.join(here, "apikey.txt")
    if os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            k = f.read().strip()
        if k:
            return k
    raise SystemExit(
        "No API key found. Set the FOOTBALL_DATA_API_KEY environment variable, "
        "or put your football-data.org key in apikey.txt next to this script."
    )

WIN, DRAW, LOSS = 3, 1, -1

# Tracked teams keyed by football-data team id (stable across name spellings).
# `flag` is an emoji fallback; the page prefers the real crest image from the API.
PLAYERS = [
    {
        "name": "Nicha",
        "color": "#ff5d8f",
        "teams": [
            {"id": 760, "name": "Spain",         "tla": "ESP", "flag": "\U0001F1EA\U0001F1F8"},
            {"id": 772, "name": "South Korea",   "tla": "KOR", "flag": "\U0001F1F0\U0001F1F7"},
            {"id": 762, "name": "Argentina",     "tla": "ARG", "flag": "\U0001F1E6\U0001F1F7"},
            {"id": 771, "name": "United States", "tla": "USA", "flag": "\U0001F1FA\U0001F1F8"},
        ],
    },
    {
        "name": "Daniele",
        "color": "#3da5ff",
        "teams": [
            {"id": 759, "name": "Germany",  "tla": "GER", "flag": "\U0001F1E9\U0001F1EA"},
            {"id": 766, "name": "Japan",    "tla": "JPN", "flag": "\U0001F1EF\U0001F1F5"},
            {"id": 769, "name": "Mexico",   "tla": "MEX", "flag": "\U0001F1F2\U0001F1FD"},
            {"id": 818, "name": "Colombia", "tla": "COL", "flag": "\U0001F1E8\U0001F1F4"},
        ],
    },
]

COUNTED_STATUSES = ("FINISHED", "AWARDED")


def fetch_matches():
    headers = {
        "X-Auth-Token": load_api_key(),
        "User-Agent": "worldcup-game/1.0 (+https://github.com)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(API_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("matches", [])


def team_record(team_id, matches):
    """Build the match list + tally (points, W, D, L) for one team."""
    records = []
    pts = w = d = l = 0
    crest = None
    for m in matches:
        home, away = m["homeTeam"], m["awayTeam"]
        if team_id not in (home.get("id"), away.get("id")):
            continue
        is_home = home.get("id") == team_id
        me, opp = (home, away) if is_home else (away, home)
        if crest is None:
            crest = me.get("crest")
        ft = m.get("score", {}).get("fullTime", {})
        gf = ft.get("home") if is_home else ft.get("away")
        ga = ft.get("away") if is_home else ft.get("home")
        status = m.get("status")
        winner = m.get("score", {}).get("winner")

        result, mpts = None, 0
        counted = status in COUNTED_STATUSES and winner is not None
        if counted:
            if winner == "DRAW":
                result, mpts = "D", DRAW
                d += 1
            elif (winner == "HOME_TEAM") == is_home:
                result, mpts = "W", WIN
                w += 1
            else:
                result, mpts = "L", LOSS
                l += 1
            pts += mpts

        records.append({
            "opponent": opp.get("name"),
            "opponentTla": opp.get("tla"),
            "opponentCrest": opp.get("crest"),
            "utcDate": m.get("utcDate"),
            "status": status,
            "stage": m.get("stage"),
            "group": m.get("group"),
            "isHome": is_home,
            "goalsFor": gf,
            "goalsAgainst": ga,
            "result": result,
            "points": mpts,
            "counted": counted,
        })
    records.sort(key=lambda r: r["utcDate"] or "")
    return records, pts, w, d, l, crest


def build_feeds(matches, tracked):
    """Consolidated recent (finished/live) and upcoming match feeds across all
    tracked teams. Each match appears once; a match between two tracked teams
    carries two 'stakes' (a head-to-head)."""
    recent, upcoming = [], []
    for m in matches:
        home, away = m["homeTeam"], m["awayTeam"]
        hid, aid = home.get("id"), away.get("id")
        if hid not in tracked and aid not in tracked:
            continue
        ft = m.get("score", {}).get("fullTime", {})
        gh, ga = ft.get("home"), ft.get("away")
        winner = m.get("score", {}).get("winner")
        status = m.get("status")
        counted = status in COUNTED_STATUSES and winner is not None

        stakes = []
        for tid, is_home in ((hid, True), (aid, False)):
            if tid in tracked:
                info = tracked[tid]
                result, pts = None, 0
                if counted:
                    if winner == "DRAW":
                        result, pts = "D", DRAW
                    elif (winner == "HOME_TEAM") == is_home:
                        result, pts = "W", WIN
                    else:
                        result, pts = "L", LOSS
                stakes.append({
                    "player": info["player"], "color": info["color"],
                    "team": info["team"]["name"], "tla": info["team"]["tla"],
                    "isHome": is_home, "result": result, "points": pts,
                })

        entry = {
            "id": m.get("id"),
            "utcDate": m.get("utcDate"),
            "status": status,
            "stage": m.get("stage"),
            "group": m.get("group"),
            "home": {"name": home.get("name"), "tla": home.get("tla"), "crest": home.get("crest")},
            "away": {"name": away.get("name"), "tla": away.get("tla"), "crest": away.get("crest")},
            "scoreHome": gh, "scoreAway": ga,
            "stakes": stakes,
            "headToHead": len(stakes) > 1,
        }
        if counted or status in ("IN_PLAY", "PAUSED"):
            recent.append(entry)
        elif status in ("SCHEDULED", "TIMED"):
            upcoming.append(entry)

    recent.sort(key=lambda e: e["utcDate"] or "", reverse=True)
    upcoming.sort(key=lambda e: e["utcDate"] or "")
    return recent, upcoming


def _ft(m):
    s = m.get("score", {}).get("fullTime", {})
    return s.get("home"), s.get("away")


def build_curiosities(matches, players_out):
    """Fun, data-driven stats for the 'curiosities' section."""
    fin = [m for m in matches
           if m.get("status") in COUNTED_STATUSES and _ft(m)[0] is not None]
    cur = []
    played = len(fin)
    if played:
        goals = sum((_ft(m)[0] or 0) + (_ft(m)[1] or 0) for m in fin)
        cur.append({"icon": "⚽", "label": "Goals so far", "value": f"{goals} in {played} games"})
        cur.append({"icon": "\U0001F4CA", "label": "Goals per game", "value": f"{goals / played:.1f}"})

        def margin(m):
            h, a = _ft(m)
            return abs((h or 0) - (a or 0))

        bw = max(fin, key=margin)
        h, a = _ft(bw)
        if (h or 0) >= (a or 0):
            val = f'{bw["homeTeam"]["tla"]} {h}–{a} {bw["awayTeam"]["tla"]}'
        else:
            val = f'{bw["awayTeam"]["tla"]} {a}–{h} {bw["homeTeam"]["tla"]}'
        cur.append({"icon": "\U0001F4A5", "label": "Biggest win", "value": val})

        def total(m):
            h, a = _ft(m)
            return (h or 0) + (a or 0)

        wg = max(fin, key=total)
        h, a = _ft(wg)
        cur.append({"icon": "\U0001F525", "label": "Wildest game",
                    "value": f'{wg["homeTeam"]["tla"]} {h}–{a} {wg["awayTeam"]["tla"]}'})

        draws = sum(1 for m in fin if m.get("score", {}).get("winner") == "DRAW")
        cur.append({"icon": "\U0001F91D", "label": "Draws so far", "value": str(draws)})

    def player_goals(p):
        return sum(r["goalsFor"] or 0
                   for t in p["teams"] for r in t["matches"]
                   if r["counted"] and r["goalsFor"] is not None)

    if len(players_out) >= 2:
        a, b = players_out[0], players_out[1]
        cur.append({"icon": "\U0001F3AF", "label": "Your teams' goals",
                    "value": f'{a["name"]} {player_goals(a)} · {b["name"]} {player_goals(b)}'})
        def team_gd_gf(t):
            gf = sum(r["goalsFor"] or 0 for r in t["matches"] if r["counted"])
            ga = sum(r["goalsAgainst"] or 0 for r in t["matches"] if r["counted"])
            return gf - ga, gf

        best = None
        for p in players_out:
            for t in p["teams"]:
                gd, gf = team_gd_gf(t)
                k = (t["points"], gd, gf)
                if best is None or k > best[0]:
                    best = (k, t)
        if best:
            t = best[1]
            cur.append({"icon": "⭐", "label": "Top team",
                        "value": f'{t["name"]} ({t["points"]:+d})'})
    return cur


def build():
    matches = fetch_matches()

    tracked = {}
    for p in PLAYERS:
        for t in p["teams"]:
            tracked[t["id"]] = {"player": p["name"], "color": p["color"], "team": t}

    players_out = []
    for p in PLAYERS:
        teams_out = []
        total = 0
        for t in p["teams"]:
            recs, pts, w, d, l, crest = team_record(t["id"], matches)
            teams_out.append({
                **t,
                "crest": crest,
                "points": pts,
                "w": w, "d": d, "l": l,
                "matches": recs,
            })
            total += pts
        players_out.append({
            "name": p["name"],
            "color": p["color"],
            "total": total,
            "teams": teams_out,
        })

    recent, upcoming = build_feeds(matches, tracked)
    curiosities = build_curiosities(matches, players_out)

    return {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "competition": "FIFA World Cup 2026",
        "rules": {"win": WIN, "draw": DRAW, "loss": LOSS},
        "players": players_out,
        "recent": recent,
        "upcoming": upcoming,
        "curiosities": curiosities,
    }


def main():
    try:
        out = build()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print(f"HTTP error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - surface any failure to the cron log
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "data.json")

    # Skip the write entirely if nothing but the timestamp would change, so the
    # cron job only commits/pushes when a real result or fixture actually moves.
    new_cmp = {k: v for k, v in out.items() if k != "updatedAt"}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                old_cmp = {k: v for k, v in json.load(f).items() if k != "updatedAt"}
            if old_cmp == new_cmp:
                totals = " | ".join(f"{p['name']} {p['total']:+d}" for p in out["players"])
                print(f"No changes. {totals}")
                return
        except Exception:
            pass  # unreadable / old format -> fall through and rewrite

    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for p in out["players"]:
        print(f"{p['name']}: {p['total']:+d} pts")
        for t in p["teams"]:
            print(f"  {t['name']:<15} {t['points']:+d}  ({t['w']}W {t['d']}D {t['l']}L)")
    print(f"Wrote {path} at {out['updatedAt']}")


if __name__ == "__main__":
    main()
