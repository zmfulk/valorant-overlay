import json
import os
import tkinter as tk
from tkinter import filedialog, ttk
import base64
import mimetypes

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "overlay_data.json")

class FastValorantController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PFW Valorant Overlay Controller")
        self.geometry("450x550")
        self.image_cache = {}  # Prevents lag by saving encoded images in memory

        self.data = self.load_data()
        self.build_ui()
        self.save_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def image_to_base64(self, path):
        if not path or not isinstance(path, str):
            return ""
            
        # FIX: If the path is ALREADY a massive base64 string, ignore file checks
        if path.startswith("data:image"):
            return path

        if path in self.image_cache:
            return self.image_cache[path]
            
        if not os.path.isfile(path):
            return path
            
        try:
            mime_type, _ = mimetypes.guess_type(path)
            mime_type = mime_type or "image/png"
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            encoded = f"data:{mime_type};base64,{b64}"
            self.image_cache[path] = encoded  # Save to memory
            return encoded
        except Exception:
            return path

    def save_data(self):
        self.data["match_phase"] = self.phase.get()
        self.data["match_meta"] = self.meta.get()
        
        self.data["show_map"] = self.show_map_var.get()
        self.data["current_map"] = self.map_name.get().upper()
        
        self.data["show_league"] = self.show_league_var.get()
        selected_league = self.league_combo.get()
        self.data["league_name"] = selected_league
        self.data["show_team_logos"] = self.show_team_logos_var.get()
        
        # Auto-load league logo
        if selected_league == "NACE":
            self.data["league_logo"] = self.image_to_base64("nace.png")
        elif selected_league == "GLEC":
            self.data["league_logo"] = self.image_to_base64("glec.png")
        else:
            self.data["league_logo"] = ""

        self.data["team1_name"] = self.t1_name.get()
        self.data["team1_score"] = int(self.t1_score.get())
        
        # FIX: Save the short path for the GUI, but generate the Base64 for OBS
        t1_path = self.t1_logo.get()
        self.data["team1_logo_path"] = t1_path
        self.data["team1_logo"] = self.image_to_base64(t1_path)

        self.data["team2_name"] = self.t2_name.get()
        self.data["team2_score"] = int(self.t2_score.get())
        
        # FIX: Save the short path for the GUI, but generate the Base64 for OBS
        t2_path = self.t2_logo.get()
        self.data["team2_logo_path"] = t2_path
        self.data["team2_logo"] = self.image_to_base64(t2_path)

        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def change_score(self, team, delta):
        entry = self.t1_score if team == 1 else self.t2_score
        val = max(0, int(entry.get() or 0) + delta)
        entry.delete(0, tk.END)
        entry.insert(0, str(val))
        self.save_data()

    def swap_teams(self):
        t1_n, t2_n = self.t1_name.get(), self.t2_name.get()
        t1_s, t2_s = self.t1_score.get(), self.t2_score.get()
        t1_l, t2_l = self.t1_logo.get(), self.t2_logo.get()

        self.t1_name.delete(0, tk.END); self.t1_name.insert(0, t2_n)
        self.t2_name.delete(0, tk.END); self.t2_name.insert(0, t1_n)
        
        self.t1_score.delete(0, tk.END); self.t1_score.insert(0, t2_s)
        self.t2_score.delete(0, tk.END); self.t2_score.insert(0, t1_s)
        
        self.t1_logo.delete(0, tk.END); self.t1_logo.insert(0, t2_l)
        self.t2_logo.delete(0, tk.END); self.t2_logo.insert(0, t1_l)
        self.save_data()

    def reset_scores(self):
        self.t1_score.delete(0, tk.END); self.t1_score.insert(0, "0")
        self.t2_score.delete(0, tk.END); self.t2_score.insert(0, "0")
        self.save_data()

    def pick_logo(self, entry_widget):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
            self.save_data()

    def build_ui(self):
        pad = {'padx': 10, 'pady': 5}
        
        # --- Match Info ---
        frame_match = tk.LabelFrame(self, text="Center Info & Toggles")
        frame_match.pack(fill="x", **pad)
        
        tk.Label(frame_match, text="Phase:").grid(row=0, column=0, sticky="w")
        self.phase = tk.Entry(frame_match, width=30)
        self.phase.insert(0, self.data.get("match_phase", "Finals"))
        self.phase.grid(row=0, column=1, sticky="w")

        tk.Label(frame_match, text="Format:").grid(row=1, column=0, sticky="w")
        self.meta = tk.Entry(frame_match, width=30)
        self.meta.insert(0, self.data.get("match_meta", "BEST OF 3"))
        self.meta.grid(row=1, column=1, sticky="w")

        self.show_map_var = tk.BooleanVar(value=self.data.get("show_map", True))
        tk.Checkbutton(frame_match, text="Show Map:", variable=self.show_map_var).grid(row=2, column=0, sticky="w")
        self.map_name = tk.Entry(frame_match, width=30)
        self.map_name.insert(0, self.data.get("current_map", "ASCENT"))
        self.map_name.grid(row=2, column=1, sticky="w")

        self.show_league_var = tk.BooleanVar(value=self.data.get("show_league", True))
        tk.Checkbutton(frame_match, text="Show League:", variable=self.show_league_var).grid(row=3, column=0, sticky="w")
        self.league_combo = ttk.Combobox(frame_match, values=["NACE", "GLEC"], state="readonly", width=27)
        self.league_combo.set(self.data.get("league_name", "NACE"))
        self.league_combo.grid(row=3, column=1, sticky="w")

        # Team Logos Toggle
        self.show_team_logos_var = tk.BooleanVar(value=self.data.get("show_team_logos", True))
        tk.Checkbutton(frame_match, text="Show Team Logos:", variable=self.show_team_logos_var).grid(row=4, column=0, sticky="w")

        # --- Team 1 ---
        frame_t1 = tk.LabelFrame(self, text="Team 1 (Left)")
        frame_t1.pack(fill="x", **pad)
        
        tk.Label(frame_t1, text="Name:").grid(row=0, column=0, sticky="w")
        self.t1_name = tk.Entry(frame_t1, width=25)
        self.t1_name.insert(0, self.data.get("team1_name", "TEAM 1"))
        self.t1_name.grid(row=0, column=1, sticky="w")
        
        tk.Label(frame_t1, text="Logo:").grid(row=1, column=0, sticky="w")
        self.t1_logo = tk.Entry(frame_t1, width=25)
        self.t1_logo.insert(0, self.data.get("team1_logo_path", ""))
        self.t1_logo.grid(row=1, column=1, sticky="w")
        tk.Button(frame_t1, text="Browse", command=lambda: self.pick_logo(self.t1_logo)).grid(row=1, column=2, padx=5)

        tk.Label(frame_t1, text="Score:").grid(row=2, column=0, sticky="w")
        self.t1_score = tk.Entry(frame_t1, width=5)
        self.t1_score.insert(0, str(self.data.get("team1_score", 0)))
        self.t1_score.grid(row=2, column=1, sticky="w")
        tk.Button(frame_t1, text="+", width=3, command=lambda: self.change_score(1, 1)).grid(row=2, column=1, sticky="e")
        tk.Button(frame_t1, text="-", width=3, command=lambda: self.change_score(1, -1)).grid(row=2, column=2)

        # --- Team 2 ---
        frame_t2 = tk.LabelFrame(self, text="Team 2 (Right)")
        frame_t2.pack(fill="x", **pad)
        
        tk.Label(frame_t2, text="Name:").grid(row=0, column=0, sticky="w")
        self.t2_name = tk.Entry(frame_t2, width=25)
        self.t2_name.insert(0, self.data.get("team2_name", "TEAM 2"))
        self.t2_name.grid(row=0, column=1, sticky="w")
        
        tk.Label(frame_t2, text="Logo:").grid(row=1, column=0, sticky="w")
        self.t2_logo = tk.Entry(frame_t2, width=25)
        # FIX: Populate the GUI box with the short file path, not the base64 data
        self.t2_logo.insert(0, self.data.get("team2_logo_path", ""))
        self.t2_logo.grid(row=1, column=1, sticky="w")
        tk.Button(frame_t2, text="Browse", command=lambda: self.pick_logo(self.t2_logo)).grid(row=1, column=2, padx=5)

        tk.Label(frame_t2, text="Score:").grid(row=2, column=0, sticky="w")
        self.t2_score = tk.Entry(frame_t2, width=5)
        self.t2_score.insert(0, str(self.data.get("team2_score", 0)))
        self.t2_score.grid(row=2, column=1, sticky="w")
        tk.Button(frame_t2, text="+", width=3, command=lambda: self.change_score(2, 1)).grid(row=2, column=1, sticky="e")
        tk.Button(frame_t2, text="-", width=3, command=lambda: self.change_score(2, -1)).grid(row=2, column=2)

        # --- Actions ---
        frame_actions = tk.Frame(self)
        frame_actions.pack(fill="x", pady=10)
        
        tk.Button(frame_actions, text="Swap Teams", command=self.swap_teams, height=2).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(frame_actions, text="Reset Scores", command=self.reset_scores, height=2).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(frame_actions, text="UPDATE OVERLAY", command=self.save_data, height=2, bg="lightgreen").pack(side="left", expand=True, fill="x", padx=5)

if __name__ == "__main__":
    app = FastValorantController()
    app.mainloop()