import math, os, tkinter as tk
from tkinter import filedialog, messagebox, ttk

# class
class Star:
    def __init__(self, x: float, y: float, magnitude: float, label: str = "", color: str = "#FFD700"):
        self.x = float(x)  # 3 атрибута
        self.y = float(y)
        self.magnitude = float(magnitude)
        self.label = str(label)
        self.color = color

    # method
    def move(self, dx: float, dy: float):
        self.x += float(dx)
        self.y += float(dy)

    # method
    def distance(self, other: "Star") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    # method
    def visual_size(self, min_sz=3, max_sz=10) -> int:
        m = max(0.1, min(6.0, self.magnitude))
        t = (m - 0.1) / (6.0 - 0.1)
        size = max_sz * (1 - t) + min_sz * t
        return int(size)

    # method
    def as_row(self):
        # Сохраняем как текст: x y magnitude [label]
        return f"{self.x} {self.y} {self.magnitude}" + (f" {self.label}" if self.label else "")

# class
class StarField:
    def __init__(self):
        self.stars: list[Star] = []
        self.cluster_ids: list[int] = []
        self.palette = ["#F94144","#F3722C","#F9844A","#F9C74F","#90BE6D","#43AA8B","#577590","#277DA1","#B5179E","#7209B7"]

    # method
    def load_text(self, path: str):
        stars = []
        with open(path, "r", encoding="utf-8-sig") as f:
            line_no = 0
            for raw in f:
                line_no += 1
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                # поддержка пробелов/запятых/точек с запятой как разделителей
                norm = line.replace(",", " ").replace(";", " ")
                parts = norm.split()
                if len(parts) < 3:
                    raise ValueError(f"Строка {line_no}: минимум 3 значения (x y magnitude), получено: {line}")
                # первые 3 — числа, остальное — метка (может содержать пробелы)
                try:
                    x = float(parts[0]); y = float(parts[1]); mag = float(parts[2])
                except:
                    raise ValueError(f"Строка {line_no}: x, y, magnitude должны быть числами: {line}")
                if not (-1e6 <= x <= 1e6 and -1e6 <= y <= 1e6):
                    raise ValueError(f"Строка {line_no}: слишком большие координаты: {x},{y}")
                if not (0.0 < mag <= 20.0):
                    raise ValueError(f"Строка {line_no}: недопустимая звездная величина (0..20]: {mag}")
                label = " ".join(parts[3:]) if len(parts) > 3 else ""
                stars.append(Star(x, y, mag, label))
        self.stars = stars
        self.cluster_ids = [-1] * len(self.stars)

    # method
    def save_text(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Формат: x y magnitude [label]\n")
            for s in self.stars:
                f.write(s.as_row() + "\n")

    # method
    def segment_by_distance(self, threshold: float) -> int:
        n = len(self.stars)
        self.cluster_ids = [-1] * n
        cluster = 0
        for i in range(n):
            if self.cluster_ids[i] != -1: continue
            self.cluster_ids[i] = cluster
            stack = [i]
            while stack:
                u = stack.pop()
                for v in range(n):
                    if self.cluster_ids[v] == -1 and self.stars[u].distance(self.stars[v]) <= threshold:
                        self.cluster_ids[v] = cluster
                        stack.append(v)
            cluster += 1
        return cluster

    # method
    def colorize_by_clusters(self):
        if not self.cluster_ids or len(self.cluster_ids) != len(self.stars): return
        for s, cid in zip(self.stars, self.cluster_ids):
            s.color = self.palette[cid % len(self.palette)]

    # method
    def colorize_by_magnitude(self):
        for s in self.stars:
            m = s.magnitude
            if m <= 2.0: s.color = "#FFD700"
            elif m <= 3.5: s.color = "#F9844A"
            elif m <= 5.0: s.color = "#277DA1"
            else: s.color = "#8D99AE"

    # method
    def move_all(self, dx: float, dy: float):
        for s in self.stars:
            s.move(dx, dy)

# class
class StarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Л.р. №8 — Вариант 33: Звезды (ОПП + Tkinter)")
        self.geometry("1000x650")
        self.minsize(900, 580)
        self.configure(bg="#121826")
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style(self); style.theme_use("clam")
        style.configure("TFrame", background="#121826")
        style.configure("TLabel", background="#121826", foreground="#E6EDF3")
        style.configure("TButton", padding=8, relief="flat", background="#1F2A44", foreground="#E6EDF3")
        style.map("TButton", background=[("active", "#2A3B63")])
        style.configure("TEntry", fieldbackground="#0E1525", foreground="#E6EDF3")
        style.configure("TLabelframe", background="#121826", foreground="#E6EDF3")
        style.configure("TLabelframe.Label", background="#121826", foreground="#9DB2CE")
        self.field = StarField()
        self.columnconfigure(1, weight=1); self.rowconfigure(0, weight=1)
        self.left = ttk.Frame(self); self.left.grid(row=0, column=0, sticky="nsew", padx=(14,10), pady=14)
        self.right = ttk.Frame(self); self.right.grid(row=0, column=1, sticky="nsew", padx=(0,14), pady=14)
        self.right.rowconfigure(0, weight=1); self.right.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.right, bg="#0B1220", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self._build_controls()
        self.bind("<Up>", lambda e: self.nudge(0, +10))
        self.bind("<Down>", lambda e: self.nudge(0, -10))
        self.bind("<Left>", lambda e: self.nudge(-10, 0))
        self.bind("<Right>", lambda e: self.nudge(+10, 0))

    # method
    def _build_controls(self):
        ttk.Label(self.left, text="Объекты — Звезды", font=("Segoe UI Semibold", 16)).pack(anchor="w", pady=(0,8))
        file_box = ttk.Labelframe(self.left, text="Файлы данных (txt/csv — split)")
        file_box.pack(fill="x", pady=8)
        ttk.Button(file_box, text="Загрузить", command=self.on_load).pack(fill="x", pady=4)
        ttk.Button(file_box, text="Сохранить", command=self.on_save).pack(fill="x", pady=4)
        ttk.Label(file_box, text="Формат: x y magnitude [label]; допускаются пробел/‘,’/‘;’").pack(anchor="w", pady=(6,2))
        seg_box = ttk.Labelframe(self.left, text="Сегментация (по расстоянию)")
        seg_box.pack(fill="x", pady=8)
        row = ttk.Frame(seg_box); row.pack(fill="x", pady=4)
        ttk.Label(row, text="Порог (px):").pack(side="left")
        self.threshold_var = tk.DoubleVar(value=60.0)
        self.threshold_entry = ttk.Entry(row, width=8, textvariable=self.threshold_var); self.threshold_entry.pack(side="left", padx=6)
        ttk.Button(seg_box, text="Сегментировать", command=self.on_segment).pack(fill="x", pady=4)
        color_box = ttk.Labelframe(self.left, text="Раскраска")
        color_box.pack(fill="x", pady=8)
        ttk.Button(color_box, text="По кластерам", command=self.on_color_clusters).pack(fill="x", pady=4)
        ttk.Button(color_box, text="По яркости (magnitude)", command=self.on_color_magnitude).pack(fill="x", pady=4)
        move_box = ttk.Labelframe(self.left, text="Перемещение")
        move_box.pack(fill="x", pady=8)
        rowm = ttk.Frame(move_box); rowm.pack(fill="x", pady=4)
        ttk.Label(rowm, text="dx:").pack(side="left")
        self.dx_var = tk.DoubleVar(value=0.0); ttk.Entry(rowm, width=8, textvariable=self.dx_var).pack(side="left", padx=(4,10))
        ttk.Label(rowm, text="dy:").pack(side="left")
        self.dy_var = tk.DoubleVar(value=0.0); ttk.Entry(rowm, width=8, textvariable=self.dy_var).pack(side="left", padx=4)
        ttk.Button(move_box, text="Сдвинуть всё", command=self.on_move).pack(fill="x", pady=4)
        ttk.Label(move_box, text="Подсказка: стрелки ←↑→↓ смещают сцену на 10 px").pack(anchor="w", pady=(6,0))
        self.legend = tk.Text(self.left, width=28, height=16, bg="#0E1525", fg="#E6EDF3", highlightthickness=0, relief="flat", font=("Consolas", 10))
        self.legend.pack(fill="both", expand=False, pady=(10,0)); self.legend.config(state="disabled")
        ttk.Label(self.left, text="Л.р. №8 (ООП, Tkinter), вариант 33").pack(anchor="w", pady=8)

    # method
    def on_load(self):
        path = filedialog.askopenfilename(
            title="Выберите файл с данными звёзд",
            filetypes=[("Текстовые файлы","*.txt"),("CSV файлы","*.csv"),("Все файлы","*.*")]
        )
        if not path: return
        try:
            self.field.load_text(path)
            self._info(f"Загружено: {len(self.field.stars)} звёзд")
            self.redraw(); self.update_legend()
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    # method
    def on_save(self):
        if not self.field.stars:
            messagebox.showwarning("Пусто", "Нет данных для сохранения."); return
        path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы","*.txt"),("CSV файлы","*.csv")]
        )
        if not path: return
        try:
            self.field.save_text(path)
            self._info(f"Сохранено в: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    # method
    def on_segment(self):
        if not self.field.stars:
            messagebox.showwarning("Пусто", "Сначала загрузите данные."); return
        try:
            thr = float(self.threshold_var.get())
            if thr <= 0: raise ValueError
        except:
            messagebox.showerror("Ошибка", "Порог расстояния должен быть положительным числом."); return
        k = self.field.segment_by_distance(thr)
        self._info(f"Найдено кластеров: {k}")
        self.update_legend(); self.redraw()

    # method
    def on_color_clusters(self):
        if not self.field.stars: return
        self.field.colorize_by_clusters(); self.redraw()

    # method
    def on_color_magnitude(self):
        if not self.field.stars: return
        self.field.colorize_by_magnitude(); self.redraw()

    # method
    def on_move(self):
        if not self.field.stars: return
        try:
            dx = float(self.dx_var.get()); dy = float(self.dy_var.get())
        except:
            messagebox.showerror("Ошибка", "dx и dy должны быть числами."); return
        self.field.move_all(dx, dy); self.redraw()

    # method
    def nudge(self, dx, dy):
        if not self.field.stars: return
        self.field.move_all(dx, dy); self.redraw()

    # method
    def redraw(self):
        self.canvas.delete("all")
        w = max(10, self.canvas.winfo_width()); h = max(10, self.canvas.winfo_height())
        cx, cy = w // 2, h // 2
        self.canvas.create_line(0, cy, w, cy, fill="#22314F")
        self.canvas.create_line(cx, 0, cx, h, fill="#22314F")
        for tick in range(-5, 6):
            x = cx + tick * 50; y = cy + tick * 50
            self.canvas.create_line(x, cy - 5, x, cy + 5, fill="#22314F")
            self.canvas.create_line(cx - 5, y, cx + 5, y, fill="#22314F")
        for i, s in enumerate(self.field.stars):
            r = s.visual_size()
            x0 = cx + s.x - r; y0 = cy - s.y - r
            x1 = cx + s.x + r; y1 = cy - s.y + r
            self.canvas.create_oval(x0, y0, x1, y1, fill=s.color, outline="")
            if s.label:
                self.canvas.create_text(cx + s.x + r + 6, cy - s.y, text=s.label, anchor="w", fill="#C8D4EA", font=("Segoe UI", 9))

    # method
    def update_legend(self):
        self.legend.config(state="normal"); self.legend.delete("1.0","end")
        self.legend.insert("end","Легенда / Кластеры\n","title"); self.legend.insert("end","---------------------\n")
        cid = self.field.cluster_ids
        if cid and len(cid) == len(self.field.stars):
            stats = {}
            for c in cid: stats[c] = stats.get(c, 0) + 1
            for c, cnt in sorted(stats.items(), key=lambda kv: kv[0]):
                col = self.field.palette[c % len(self.field.palette)]
                self.legend.insert("end",f"#{c:02d}: {cnt} шт.\n",(f"c{c}",)); self.legend.tag_config(f"c{c}", foreground=col)
        else:
            self.legend.insert("end","Кластеры не вычислены.\nНажмите «Сегментировать».")
        self.legend.config(state="disabled")

    # method
    def _info(self, msg: str):
        self.title(f"Л.р. №8 — Вариант 33: {msg}")

if __name__ == "__main__":
    app = StarApp()
    app.mainloop()
