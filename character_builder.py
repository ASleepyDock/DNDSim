"""
Character builder UI for DNDSim.

Enter character data, save it as the JSON format creature.py expects,
or load an existing file to edit it. Uses only the standard library.

Run:  python character_builder.py
"""
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from urllib.request import Request, urlopen

CHARACTER_DIR = Path("./Characters")
STATS = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
DAMAGE_TYPES = ["bludgeoning", "piercing", "slashing", "fire", "cold", "lightning",
                "thunder", "acid", "poison", "necrotic", "radiant", "force", "psychic"]
DDB_URL = "https://character-service.dndbeyond.com/character/v5/character/{}"


# ---------------------------------------------------------------- D&D Beyond
def fetch_ddb_character(character_id: int) -> dict:
    """Download the raw D&D Beyond JSON (character sheet must be public)."""
    req = Request(DDB_URL.format(character_id), headers={"User-Agent": "DNDSim"})
    with urlopen(req, timeout=10) as resp:
        return json.load(resp)


def ddb_to_sim_json(raw: dict) -> dict:
    """
    Convert a D&D Beyond response into DNDSim's format.
    TODO: needs a real response to map against (stats, HP, AC and weapon
    bonuses are spread across several fields and modifiers).
    """
    raise NotImplementedError("D&D Beyond mapping not written yet")


# ------------------------------------------------------------------ Weapon row
class WeaponRow:
    def __init__(self, parent, row, on_remove):
        self.vars = {
            "name": tk.StringVar(),
            "priority": tk.StringVar(value="1"),
            "bonus": tk.StringVar(value="0"),
            "damageDie": tk.StringVar(value="6"),
            "damageModifier": tk.StringVar(value="0"),
            "damageType": tk.StringVar(value="slashing"),
            "finesse": tk.BooleanVar(value=False),
        }
        self.widgets = [
            ttk.Entry(parent, textvariable=self.vars["name"], width=16),
            ttk.Spinbox(parent, from_=1, to=99, textvariable=self.vars["priority"], width=4),
            ttk.Spinbox(parent, from_=-10, to=20, textvariable=self.vars["bonus"], width=4),
            ttk.Spinbox(parent, values=(4, 6, 8, 10, 12, 20), textvariable=self.vars["damageDie"], width=4),
            ttk.Spinbox(parent, from_=-10, to=30, textvariable=self.vars["damageModifier"], width=4),
            ttk.Combobox(parent, values=DAMAGE_TYPES, textvariable=self.vars["damageType"], width=12),
            ttk.Checkbutton(parent, variable=self.vars["finesse"]),
            ttk.Button(parent, text="✕", width=3, command=lambda: on_remove(self)),
        ]
        self.grid(row)

    def grid(self, row):
        for col, w in enumerate(self.widgets):
            w.grid(row=row, column=col, padx=2, pady=2)

    def destroy(self):
        for w in self.widgets:
            w.destroy()

    def to_dict(self):
        v = self.vars
        name = v["name"].get().strip()
        if not name:
            raise ValueError("Every weapon needs a name.")
        return {
            "name": name,
            "priority": int(v["priority"].get()),
            "bonus": int(v["bonus"].get()),
            "damageDie": int(v["damageDie"].get()),
            "damageModifier": int(v["damageModifier"].get()),
            "damageType": v["damageType"].get().strip(),
            "finesse": bool(v["finesse"].get()),
        }

    def load(self, w):
        for key, var in self.vars.items():
            var.set(w.get(key, var.get()))


# ------------------------------------------------------------------------ App
class CharacterBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DNDSim Character Builder")
        self.resizable(False, False)
        self.weapon_rows: list[WeaponRow] = []

        self.name = tk.StringVar()
        self.alignment = tk.StringVar(value="Good")
        self.monster = tk.BooleanVar(value=False)
        self.hp = tk.StringVar(value="10")
        self.ac = tk.StringVar(value="10")
        self.prof = tk.StringVar(value="2")
        self.stats = {s: tk.StringVar(value="10") for s in STATS}

        self._build()
        self.add_weapon()

    def _build(self):
        pad = {"padx": 8, "pady": 4}
        main = ttk.Frame(self)
        main.grid(sticky="nsew", **pad)

        # Basics
        basics = ttk.LabelFrame(main, text="Basics")
        basics.grid(row=0, column=0, sticky="ew", **pad)
        ttk.Label(basics, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(basics, textvariable=self.name, width=28).grid(row=0, column=1, columnspan=3, **pad)
        ttk.Label(basics, text="Alignment").grid(row=1, column=0, sticky="w")
        ttk.Combobox(basics, values=["Good", "Evil"], textvariable=self.alignment,
                     width=8, state="readonly").grid(row=1, column=1, **pad)
        ttk.Checkbutton(basics, text="Monster", variable=self.monster).grid(row=1, column=2, columnspan=2)
        for i, (label, var) in enumerate([("Max HP", self.hp), ("Armour Class", self.ac),
                                          ("Proficiency", self.prof)]):
            ttk.Label(basics, text=label).grid(row=2 + i // 2, column=(i % 2) * 2, sticky="w")
            ttk.Spinbox(basics, from_=0, to=999, textvariable=var, width=6).grid(
                row=2 + i // 2, column=(i % 2) * 2 + 1, **pad)

        # Stats
        stats = ttk.LabelFrame(main, text="Ability scores")
        stats.grid(row=1, column=0, sticky="ew", **pad)
        for i, s in enumerate(STATS):
            ttk.Label(stats, text=s[:3].upper()).grid(row=0, column=i)
            ttk.Spinbox(stats, from_=1, to=30, textvariable=self.stats[s], width=4).grid(
                row=1, column=i, padx=4, pady=4)

        # Weapons
        self.weapon_frame = ttk.LabelFrame(main, text="Weapons (highest priority is used)")
        self.weapon_frame.grid(row=2, column=0, sticky="ew", **pad)
        headers = ["Name", "Prio", "Bonus", "Die", "Dmg mod", "Type", "Finesse", ""]
        for c, h in enumerate(headers):
            ttk.Label(self.weapon_frame, text=h).grid(row=0, column=c)
        ttk.Button(main, text="+ Add weapon", command=self.add_weapon).grid(row=3, column=0, sticky="w", **pad)

        # Actions
        bar = ttk.Frame(main)
        bar.grid(row=4, column=0, sticky="ew", **pad)
        ttk.Button(bar, text="Load JSON…", command=self.load_file).pack(side="left")
        ttk.Button(bar, text="Import from D&D Beyond…", command=self.import_ddb).pack(side="left", padx=6)
        ttk.Button(bar, text="Save JSON", command=self.save_file).pack(side="right")

    # -- weapons
    def add_weapon(self):
        row = WeaponRow(self.weapon_frame, len(self.weapon_rows) + 1, self.remove_weapon)
        self.weapon_rows.append(row)
        return row

    def remove_weapon(self, row):
        row.destroy()
        self.weapon_rows.remove(row)
        for i, r in enumerate(self.weapon_rows, start=1):
            r.grid(i)

    # -- data in/out
    def collect(self) -> dict:
        name = self.name.get().strip()
        if not name:
            raise ValueError("Name is required.")
        return {"data": {
            "name": name,
            "alignment": self.alignment.get(),
            "monster": bool(self.monster.get()),
            "maximumHitPoints": int(self.hp.get()),
            "armourClass": int(self.ac.get()),
            "proficiencyBonus": int(self.prof.get()),
            "stats": {s: int(v.get()) for s, v in self.stats.items()},
            "weapons": [r.to_dict() for r in self.weapon_rows],
        }}

    def populate(self, doc: dict):
        d = doc["data"]
        self.name.set(d.get("name", ""))
        self.alignment.set(d.get("alignment", "Good"))
        self.monster.set(d.get("monster", False))
        self.hp.set(d.get("maximumHitPoints", 10))
        self.ac.set(d.get("armourClass", 10))
        self.prof.set(d.get("proficiencyBonus", 0))
        for s in STATS:
            self.stats[s].set(d.get("stats", {}).get(s, 10))
        for r in list(self.weapon_rows):
            self.remove_weapon(r)
        for w in d.get("weapons") or []:
            self.add_weapon().load(w)

    def save_file(self):
        try:
            doc = self.collect()
        except ValueError as e:
            messagebox.showerror("Invalid data", f"Please check your entries:\n{e}")
            return
        CHARACTER_DIR.mkdir(exist_ok=True)
        default = re.sub(r"\W+", "_", doc["data"]["name"].split()[0]).lower() + ".json"
        path = filedialog.asksaveasfilename(initialdir=CHARACTER_DIR, initialfile=default,
                                            defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w") as f:
                json.dump(doc, f, indent=4)
            messagebox.showinfo("Saved", f"Saved to {path}")

    def load_file(self):
        path = filedialog.askopenfilename(initialdir=CHARACTER_DIR, filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path) as f:
                    self.populate(json.load(f))
            except (OSError, KeyError, json.JSONDecodeError) as e:
                messagebox.showerror("Load failed", str(e))

    def import_ddb(self):
        win = tk.Toplevel(self)
        win.title("Import from D&D Beyond")
        ttk.Label(win, text="Character ID or URL:").grid(row=0, column=0, padx=8, pady=8)
        entry = ttk.Entry(win, width=50)
        entry.grid(row=0, column=1, padx=8, pady=8)

        def go():
            m = re.search(r"(\d+)\s*$", entry.get().strip())
            if not m:
                messagebox.showerror("Import", "Couldn't find a character ID.", parent=win)
                return
            try:
                self.populate(ddb_to_sim_json(fetch_ddb_character(int(m.group(1)))))
                win.destroy()
            except NotImplementedError as e:
                messagebox.showinfo("Import", str(e), parent=win)
            except Exception as e:
                messagebox.showerror("Import failed", str(e), parent=win)

        ttk.Button(win, text="Import", command=go).grid(row=1, column=1, sticky="e", padx=8, pady=8)


if __name__ == "__main__":
    CharacterBuilder().mainloop()
