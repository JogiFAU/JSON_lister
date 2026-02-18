import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Any, Dict, List


class JSONListerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("JSON Lister – Whitelist/Blacklist Builder")
        self.root.geometry("1100x700")

        self.data: List[Any] = []
        self.current_index = 0
        self.display_count = 1
        self.current_item: Dict[str, Any] = {}

        self.whitelist: set[str] = set()
        self.blacklist: set[str] = set()

        self._build_ui()

    def _build_ui(self) -> None:
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="JSON-Datei öffnen", command=self.load_file).pack(side=tk.LEFT)

        ttk.Label(top_frame, text="Anzahl Beispiele:").pack(side=tk.LEFT, padx=(15, 5))
        self.count_var = tk.StringVar(value="1")
        ttk.Entry(top_frame, textvariable=self.count_var, width=8).pack(side=tk.LEFT)

        ttk.Button(top_frame, text="Anwenden", command=self.apply_count).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(top_frame, text="Vorheriges", command=self.prev_item).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(top_frame, text="Nächstes", command=self.next_item).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Keine Datei geladen")
        ttk.Label(top_frame, textvariable=self.status_var).pack(side=tk.RIGHT)

        center_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Variablenübersicht
        vars_frame = ttk.LabelFrame(center_frame, text="Variablen (Tag + Wert des aktuellen Elements)", padding=10)
        vars_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.variables_list = tk.Listbox(vars_frame, selectmode=tk.EXTENDED)
        self.variables_list.pack(fill=tk.BOTH, expand=True)

        buttons_frame = ttk.Frame(vars_frame)
        buttons_frame.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(buttons_frame, text="→ Zur Whitelist", command=self.add_to_whitelist).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="→ Zur Blacklist", command=self.add_to_blacklist).pack(side=tk.LEFT, padx=6)

        # White/Blacklist
        side_frame = ttk.Frame(center_frame)
        side_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        whitelist_frame = ttk.LabelFrame(side_frame, text="Whitelist", padding=10)
        whitelist_frame.pack(fill=tk.BOTH, expand=True)
        self.whitelist_list = tk.Listbox(whitelist_frame)
        self.whitelist_list.pack(fill=tk.BOTH, expand=True)

        wl_buttons = ttk.Frame(whitelist_frame)
        wl_buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(wl_buttons, text="Ausgewählte entfernen", command=self.remove_from_whitelist).pack(side=tk.LEFT)
        ttk.Button(wl_buttons, text="Whitelist exportieren", command=lambda: self.export_list("whitelist")).pack(
            side=tk.LEFT, padx=6
        )

        blacklist_frame = ttk.LabelFrame(side_frame, text="Blacklist", padding=10)
        blacklist_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.blacklist_list = tk.Listbox(blacklist_frame)
        self.blacklist_list.pack(fill=tk.BOTH, expand=True)

        bl_buttons = ttk.Frame(blacklist_frame)
        bl_buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(bl_buttons, text="Ausgewählte entfernen", command=self.remove_from_blacklist).pack(side=tk.LEFT)
        ttk.Button(bl_buttons, text="Blacklist exportieren", command=lambda: self.export_list("blacklist")).pack(
            side=tk.LEFT, padx=6
        )

    def load_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Alle Dateien", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except Exception as err:
            messagebox.showerror("Fehler", f"Datei konnte nicht gelesen werden:\n{err}")
            return

        if isinstance(loaded, list):
            self.data = loaded
        else:
            self.data = [loaded]

        if not self.data:
            messagebox.showwarning("Hinweis", "Die JSON-Datei enthält keine Elemente.")
            return

        self.current_index = 0
        self.apply_count()
        self.status_var.set(f"Geladen: {Path(file_path).name} | Elemente: {len(self.data)}")

    def apply_count(self) -> None:
        if not self.data:
            return

        try:
            count = int(self.count_var.get())
            if count < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ungültige Eingabe", "Anzahl Beispiele muss eine positive Zahl sein.")
            self.count_var.set("1")
            return

        self.display_count = min(count, len(self.data))
        self.current_index = 0
        self.show_current_item()

    def show_current_item(self) -> None:
        self.variables_list.delete(0, tk.END)
        if not self.data:
            return

        item = self.data[self.current_index]
        if not isinstance(item, dict):
            item = {"value": item}

        self.current_item = item

        for key, value in item.items():
            short_val = json.dumps(value, ensure_ascii=False)
            self.variables_list.insert(tk.END, f"{key} = {short_val}")

        self.status_var.set(
            f"Element {self.current_index + 1}/{self.display_count} (Gesamt im Datensatz: {len(self.data)})"
        )

    def prev_item(self) -> None:
        if not self.data:
            return
        self.current_index = (self.current_index - 1) % self.display_count
        self.show_current_item()

    def next_item(self) -> None:
        if not self.data:
            return
        self.current_index = (self.current_index + 1) % self.display_count
        self.show_current_item()

    def _selected_keys(self) -> List[str]:
        selected_indices = self.variables_list.curselection()
        keys: List[str] = []
        for idx in selected_indices:
            row = self.variables_list.get(idx)
            key = row.split(" = ", 1)[0].strip()
            if key:
                keys.append(key)
        return keys

    def add_to_whitelist(self) -> None:
        keys = self._selected_keys()
        for key in keys:
            self.whitelist.add(key)
            self.blacklist.discard(key)
        self.refresh_lists()

    def add_to_blacklist(self) -> None:
        keys = self._selected_keys()
        for key in keys:
            self.blacklist.add(key)
            self.whitelist.discard(key)
        self.refresh_lists()

    def remove_from_whitelist(self) -> None:
        for idx in reversed(self.whitelist_list.curselection()):
            self.whitelist.discard(self.whitelist_list.get(idx))
        self.refresh_lists()

    def remove_from_blacklist(self) -> None:
        for idx in reversed(self.blacklist_list.curselection()):
            self.blacklist.discard(self.blacklist_list.get(idx))
        self.refresh_lists()

    def refresh_lists(self) -> None:
        self.whitelist_list.delete(0, tk.END)
        self.blacklist_list.delete(0, tk.END)

        for key in sorted(self.whitelist):
            self.whitelist_list.insert(tk.END, key)
        for key in sorted(self.blacklist):
            self.blacklist_list.insert(tk.END, key)

    def export_list(self, mode: str) -> None:
        values = sorted(self.whitelist if mode == "whitelist" else self.blacklist)
        if not values:
            messagebox.showinfo("Hinweis", f"Die {mode} ist leer.")
            return

        file_path = filedialog.asksaveasfilename(
            title=f"{mode.capitalize()} speichern",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Text", "*.txt")],
            initialfile=f"{mode}.json",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(values, f, ensure_ascii=False, indent=2)
        except Exception as err:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{err}")
            return

        messagebox.showinfo("Erfolg", f"{mode.capitalize()} exportiert nach:\n{file_path}")


def main() -> None:
    root = tk.Tk()
    app = JSONListerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
