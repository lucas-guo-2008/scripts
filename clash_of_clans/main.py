import requests
import ast
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

def get_player(player_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/players/%23{player_tag}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

response = get_player("200LVGU9V")
print(response)

# Claude's formatting work starts here

# ---------- categories the API lumps into "troops" ----------
SIEGE_MACHINES = {
    "Wall Wrecker", "Battle Blimp", "Stone Slammer", "Siege Barracks",
    "Log Launcher", "Flame Flinger", "Battle Drill", "Troop Launcher",
}
PETS = {
    "L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn", "Frosty", "Diggy",
    "Poison Lizard", "Phoenix", "Spirit Fox", "Angry Jelly", "Sneezy",
}
SUPER_TROOPS = {
    "Sneaky Goblin", "Rocket Balloon", "Inferno Dragon", "Ice Hound",
}  # plus anything starting with "Super "


def load(data):
    """Accept a dict, JSON string, or requests.Response."""
    if hasattr(data, "json"):
        return data.json()
    if isinstance(data, (str, bytes)):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return ast.literal_eval(data)  # handles Python-style dict strings
    return data


# ---------- formatting helpers ----------
def bar(value, maximum, width=20):
    if not maximum:
        return ""
    filled = min(width, round(width * value / maximum))
    return "█" * filled + "░" * (width - filled)


def header(title):
    print(f"\n{'═' * 60}\n  {title}\n{'═' * 60}")


def subheader(title):
    print(f"\n  ── {title} ──")


def level_line(name, level, max_level, indent=4, extra=""):
    tag = " ✔ MAX" if level >= max_level else ""
    print(f"{' ' * indent}{name:<24} {level:>3}/{max_level:<3} "
          f"{bar(level, max_level)}{tag}{extra}")


def section_summary(items):
    """'12/30 maxed, 74% overall' for a list of leveled items."""
    if not items:
        return ""
    maxed = sum(i["level"] >= i["maxLevel"] for i in items)
    pct = 100 * sum(i["level"] for i in items) / sum(i["maxLevel"] for i in items)
    return f"{maxed}/{len(items)} maxed · {pct:.0f}% of total levels"


def kv(label, value):
    print(f"    {label:<26} {value}")


# ---------- sections ----------
def print_profile(p):
    header(f"{p['name']}  ({p['tag']})")
    kv("Town Hall", f"{p['townHallLevel']}"
       + (f" (weapon {p['townHallWeaponLevel']})" if p.get("townHallWeaponLevel") else ""))
    kv("XP Level", p.get("expLevel"))
    kv("Trophies (best)", f"{p.get('trophies', 0):,} ({p.get('bestTrophies', 0):,})")
    if p.get("leagueTier"):
        kv("League", p["leagueTier"]["name"])
    kv("War Stars", p.get("warStars"))
    kv("War Preference", p.get("warPreference", "—"))
    kv("Donations / Received", f"{p.get('donations', 0):,} / {p.get('donationsReceived', 0):,}")
    kv("Capital Contributions", f"{p.get('clanCapitalContributions', 0):,}")

    subheader("Builder Base")
    kv("Builder Hall", p.get("builderHallLevel"))
    kv("Trophies (best)", f"{p.get('builderBaseTrophies', 0):,} "
                          f"({p.get('bestBuilderBaseTrophies', 0):,})")
    if p.get("builderBaseLeague"):
        kv("League", p["builderBaseLeague"]["name"])

    if p.get("clan"):
        c = p["clan"]
        subheader("Clan")
        kv("Name", f"{c['name']} ({c['tag']})")
        kv("Clan Level", c.get("clanLevel"))
        kv("Role", p.get("role", "—"))

    if p.get("labels"):
        kv("Labels", ", ".join(l["name"] for l in p["labels"]))


def print_heroes(p):
    heroes = p.get("heroes", [])
    for village, title in (("home", "Heroes"), ("builderBase", "Builder Base Heroes")):
        group = [h for h in heroes if h["village"] == village]
        if not group:
            continue
        header(f"{title}  —  {section_summary(group)}")
        for h in group:
            level_line(h["name"], h["level"], h["maxLevel"])
            for eq in h.get("equipment", []):
                level_line("↳ " + eq["name"], eq["level"], eq["maxLevel"], indent=8)


def print_equipment(p):
    eq = p.get("heroEquipment", [])
    if not eq:
        return
    equipped = {e["name"] for h in p.get("heroes", []) for e in h.get("equipment", [])}
    header(f"Hero Equipment  —  {section_summary(eq)}")
    for e in sorted(eq, key=lambda e: (-e["maxLevel"], -e["level"])):
        level_line(e["name"], e["level"], e["maxLevel"],
                   extra="  (equipped)" if e["name"] in equipped else "")


def print_troops(p):
    troops = p.get("troops", [])
    home = [t for t in troops if t["village"] == "home"]

    def is_super(t):
        return t["name"].startswith("Super ") or t["name"] in SUPER_TROOPS

    groups = {
        "Troops": [t for t in home if not is_super(t)
                   and t["name"] not in SIEGE_MACHINES and t["name"] not in PETS],
        "Siege Machines": [t for t in home if t["name"] in SIEGE_MACHINES],
        "Pets": [t for t in home if t["name"] in PETS],
    }
    for title, items in groups.items():
        if items:
            header(f"{title}  —  {section_summary(items)}")
            for t in items:
                level_line(t["name"], t["level"], t["maxLevel"])

    # Super troop levels just mirror the base troop, so only show what's boosted
    active = [t["name"] for t in home if is_super(t) and t.get("superTroopIsActive")]
    header("Super Troops")
    print(f"    Currently boosted: {', '.join(active) if active else 'none'}")

    builder = [t for t in troops if t["village"] == "builderBase"]
    if builder:
        header(f"Builder Base Troops  —  {section_summary(builder)}")
        for t in builder:
            level_line(t["name"], t["level"], t["maxLevel"])


def print_spells(p):
    spells = p.get("spells", [])
    if spells:
        header(f"Spells  —  {section_summary(spells)}")
        for s in spells:
            level_line(s["name"], s["level"], s["maxLevel"])


def print_achievements(p):
    ach = p.get("achievements", [])
    if not ach:
        return
    # one-off achievements (e.g. account linking) report 0 stars but "Completed!"
    def is_done(a):
        return a["stars"] == 3 or a.get("completionInfo") == "Completed!"

    done = [a for a in ach if is_done(a)]
    todo = [a for a in ach if not is_done(a)]
    header(f"Achievements  —  {len(done)}/{len(ach)} complete")

    subheader("In progress (closest first)")
    for a in sorted(todo, key=lambda a: -a["value"] / a["target"] if a["target"] else 0):
        stars = "★" * a["stars"] + "☆" * (3 - a["stars"])
        pct = min(100, 100 * a["value"] / a["target"]) if a["target"] else 0
        print(f"    {stars} {a['name']:<30} {a['value']:>10,} / {a['target']:<10,} "
              f"{bar(a['value'], a['target'], 15)} {pct:3.0f}%")
        print(f"          {a['info']}")

    subheader("Completed")
    for a in done:
        stars = "★" * a["stars"] + "☆" * (3 - a["stars"])
        print(f"    {stars} {a['name']:<30} {a.get('completionInfo') or ''}")


def format_player(data):
    p = load(data)
    print_profile(p)
    print_heroes(p)
    print_equipment(p)
    print_troops(p)
    print_spells(p)
    print_achievements(p)
    print()


format_player(response)