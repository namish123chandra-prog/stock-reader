# ============================================================
#  THE APP WINDOW (modern theme, built with tkinter)
#  Buttons are created automatically from the features folder.
#  Choose dark/light with the Theme button (saved in theme.json).
# ============================================================

import datetime
import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font

from core.app import App
from core.persistence import BASE, read_json

DARK = {
    "bg": "#0b1220", "panel": "#111c30", "header": "#0e1728",
    "text": "#e8eef7", "muted": "#8ea3c0", "entry": "#1a2942",
    "bubble": "#1e2d47", "pill": "#27324a", "pill_live": "#14532d",
}
LIGHT = {
    "bg": "#eef3fa", "panel": "#ffffff", "header": "#dce7f7",
    "text": "#0f172a", "muted": "#5b6b82", "entry": "#ffffff",
    "bubble": "#e7eefb", "pill": "#cbd6e8", "pill_live": "#c9f2d8",
}

BLUE, SKY, GREEN, TEAL = "#3b82f6", "#0ea5e9", "#22c55e", "#14b8a6"
PURPLE, ORANGE, RED = "#8b5cf6", "#f59e0b", "#ef4444"
HOVER = {
    BLUE: "#5b9bff", SKY: "#38bdf8", GREEN: "#4ade80", TEAL: "#2dd4bf",
    PURPLE: "#a78bfa", ORANGE: "#fbbf24", RED: "#ff7070",
}
CHIP_COLORS = {
    "SOS": RED, "News": SKY, "Today's Market": PURPLE,
    "My Stocks": GREEN, "Best Stocks Today": ORANGE,
    "Check a Stock": BLUE, "Check Big Drops": RED,
    "Send Hi": TEAL, "Phone Chat Setup": PURPLE,
    "Watchlist": TEAL, "Price Targets": ORANGE, "Compare": BLUE,
    "SIP Calc": GREEN, "Close Report": PURPLE, "Backup": SKY,
    "Theme": ORANGE, "Info": BLUE,
}
FONT = "Segoe UI"

TIPS = [
    "Tip: spreading money across different stocks is safer than putting it all in one.",
    "Tip: a share is a tiny slice of a company - you own a bit of it!",
    "Tip: Nifty is a scoreboard of India's 50 biggest companies.",
    "Tip: never invest money you'll need next month for school fees or bills.",
    "Tip: a falling price isn't always bad news - check the full story first.",
]


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class BuddyGUI:
    def __init__(self, app: App):
        self.app = app
        self.q = queue.Queue()
        self._thinking = None
        self._transcript = []
        palette = LIGHT if read_json("theme.json", {}).get("theme") == "light" \
            else DARK
        self.C = palette  # short name for the colour palette

        self.root = tk.Tk()
        self.root.title("Stock Buddy - Indian Stock Helper")
        self.root.geometry("850x720")
        self.root.minsize(700, 540)
        self.root.configure(bg=self.C["bg"])

        self._build_header()
        self._build_buttons()
        self._build_chat()
        self._build_input()

        tk.Label(self.root,
                 text="Learning helper, not guaranteed advice  •  Prices may be "
                      "~15 min delayed  •  Big decisions? Ask a parent/guardian",
                 font=(FONT, 8), fg=self.C["muted"], bg=self.C["bg"]
                 ).pack(pady=(2, 6))

        self.app.alert_listeners.append(self._on_alert)
        tip = TIPS[datetime.date.today().timetuple().tm_yday % len(TIPS)]
        self._append("Stock Buddy",
                     "Hey! I watch India's big stocks for you while you're at "
                     "school.\nPress a button above, or type things like "
                     "'should I buy reliance?', 'what is a dividend?' or 'help'.\n\n"
                     + tip, "buddy")
        self._update_market_label()
        self.root.after(150, self._drain_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.entry.focus_set()

    # ---- construction -----------------------------------------
    def _build_header(self):
        head = tk.Frame(self.root, bg=self.C["header"], height=84)
        head.pack(fill="x")
        head.pack_propagate(False)
        accent = tk.Canvas(head, bg=self.C["header"], highlightthickness=0,
                           height=4)
        accent.pack(fill="x", side="bottom")
        accent.create_rectangle(0, 0, 260, 4, fill=SKY, outline="")
        accent.create_rectangle(260, 0, 520, 4, fill=PURPLE, outline="")
        accent.create_rectangle(520, 0, 850, 4, fill=GREEN, outline="")

        left = tk.Frame(head, bg=self.C["header"])
        left.pack(side="left", padx=20, pady=12)
        tk.Label(left, text="STOCK BUDDY", font=(FONT, 19, "bold"),
                 fg=self.C["text"], bg=self.C["header"]).pack(anchor="w")
        tk.Label(left, text="simple Indian stock helper  •  always watching",
                 font=(FONT, 9), fg=self.C["muted"], bg=self.C["header"]
                 ).pack(anchor="w")

        self.market_pill = tk.Canvas(head, bg=self.C["header"],
                                     highlightthickness=0, width=240, height=30)
        self.market_pill.pack(side="right", padx=20)
        self.pill_box = rounded_rect(self.market_pill, 1, 1, 239, 29, 14,
                                     fill=self.C["pill"], outline="")
        self.pill_text = self.market_pill.create_text(
            120, 15, text="checking market...", fill=self.C["text"],
            font=(FONT, 9, "bold"))

    def _build_buttons(self):
        area = tk.Frame(self.root, bg=self.C["bg"])
        area.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(area, text="QUICK ACTIONS", font=(FONT, 8, "bold"),
                 fg=self.C["muted"], bg=self.C["bg"]).pack(anchor="w")
        grid = tk.Frame(area, bg=self.C["bg"])
        grid.pack(fill="x", pady=(4, 0))
        col = 0
        for feature in self.app.features:
            if not feature.button:
                continue
            color = CHIP_COLORS.get(feature.button, BLUE)
            chip = self._chip(grid, feature.button, color,
                              lambda f=feature: self._run_button(f))
            chip.grid(row=col // 5, column=col % 5, padx=4, pady=4, sticky="w")
            col += 1
        for i in range(5):
            grid.grid_columnconfigure(i, weight=1)

    def _chip(self, parent, label, color, command):
        font = Font(family=FONT, size=9, weight="bold")
        w, h = font.measure(label) + 28, 31
        c = tk.Canvas(parent, bg=self.C["bg"], highlightthickness=0,
                      width=w, height=h, cursor="hand2")
        box = rounded_rect(c, 1, 1, w - 1, h - 1, 9, fill=color, outline="")
        c.create_text(w / 2, h / 2, text=label, fill="white", font=font)
        c.bind("<Enter>", lambda e: c.itemconfig(box,
                                                 fill=HOVER.get(color, color)))
        c.bind("<Leave>", lambda e: c.itemconfig(box, fill=color))
        c.bind("<Button-1>", lambda e: command())
        return c

    def _build_chat(self):
        panel = tk.Frame(self.root, bg=self.C["panel"])
        panel.pack(fill="both", expand=True, padx=16, pady=6)

        self.chat_canvas = tk.Canvas(panel, bg=self.C["panel"],
                                     highlightthickness=0)
        scroll = tk.Scrollbar(panel, orient="vertical",
                              command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)

        self.messages = tk.Frame(self.chat_canvas, bg=self.C["panel"])
        self._window_item = self.chat_canvas.create_window(
            (0, 0), window=self.messages, anchor="nw")
        self.messages.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", self._on_canvas_resize)

    def _build_input(self):
        bar = tk.Frame(self.root, bg=self.C["bg"])
        bar.pack(fill="x", padx=16, pady=(4, 2))

        self.entry = tk.Entry(bar, font=(FONT, 11), bg=self.C["entry"],
                              fg=self.C["text"], insertbackground=self.C["text"],
                              bd=0, relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=9,
                        padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._send())

        save = tk.Button(bar, text="Save Chat", font=(FONT, 8),
                         fg=self.C["muted"], bg=self.C["bg"], bd=0,
                         activeforeground=self.C["text"],
                         activebackground=self.C["bg"], cursor="hand2",
                         command=self._export_chat)
        save.pack(side="right", padx=(0, 8))

        font = Font(family=FONT, size=10, weight="bold")
        w = font.measure("Send") + 40
        send = tk.Canvas(bar, bg=self.C["bg"], highlightthickness=0,
                         width=w, height=36, cursor="hand2")
        box = rounded_rect(send, 1, 1, w - 1, 35, 10, fill=GREEN, outline="")
        send.create_text(w / 2, 18, text="Send", fill="white", font=font)
        send.bind("<Enter>", lambda e: send.itemconfig(box, fill=HOVER[GREEN]))
        send.bind("<Leave>", lambda e: send.itemconfig(box, fill=GREEN))
        send.bind("<Button-1>", lambda e: self._send())
        send.pack(side="right")

    # ---- chat bubbles -------------------------------------------
    def _on_canvas_resize(self, event):
        self.chat_canvas.itemconfig(self._window_item, width=event.width)

    def _bubble(self, who, text, kind):
        row = tk.Frame(self.messages, bg=self.C["panel"])
        row.pack(fill="x", padx=14, pady=5)

        width = max(300, self.chat_canvas.winfo_width() - 130)
        c = tk.Canvas(row, bg=self.C["panel"], highlightthickness=0)

        if kind == "user":
            fill, fg, tag_color = BLUE, "white", "#bfdbfe"
        elif kind == "alert":
            fill, fg, tag_color = "#7f1d1d", "#fee2e2", "#ff9b9b"
        else:
            fill, fg, tag_color = self.C["bubble"], self.C["text"], SKY

        if who:
            c.create_text(14, 14, anchor="nw", text=who.upper(),
                          fill=tag_color, font=(FONT, 8, "bold"))
        top = 32 if who else 12
        msg = c.create_text(14, top, anchor="nw", text=text, fill=fg,
                            font=(FONT, 10), width=width - 28)
        c.update_idletasks()
        bbox = c.bbox(msg)
        h = (bbox[3] if bbox else top + 20) + 14
        bubble_w = min(width, max(170, (bbox[2] if bbox else width) + 16))
        c.configure(width=bubble_w, height=h)
        box = rounded_rect(c, 0, 0, bubble_w, h, 12, fill=fill, outline="")
        c.tag_lower(box)
        c.pack(side="right" if kind == "user" else "left")
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        return row

    def _append(self, who, text, tag):
        self._transcript.append(f"{who or 'Buddy'}: {text}\n")
        self._bubble(who, text, tag)
        self.chat_canvas.yview_moveto(1.0)

    def _export_chat(self):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BASE, f"chat_export_{stamp}.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write("STOCK BUDDY - CHAT EXPORT\n\n" + "".join(self._transcript))
        messagebox.showinfo("Saved", f"Chat saved to:\n{dest}")

    # ---- actions -------------------------------------------------
    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._append("You", text, "user")
        self._show_thinking()
        threading.Thread(target=self._work, args=(self.app.handle, text),
                         daemon=True).start()

    def _run_button(self, feature):
        self._append("You", f"[ {feature.button} ]", "user")
        self._show_thinking()
        threading.Thread(target=self._work,
                         args=(self.app.press_button, feature),
                         daemon=True).start()

    def _show_thinking(self):
        self._thinking = self._bubble("", "Buddy is thinking...", "buddy")

    def _work(self, fn, arg):
        try:
            answer = fn(arg)
        except Exception as e:
            answer = f"Something went wrong: {e}\nCheck your internet and try again."
        self.q.put(("answer", answer))

    def _on_alert(self, text):
        self.q.put(("alert", text))

    def _drain_queue(self):
        try:
            while True:
                kind, text = self.q.get_nowait()
                if self._thinking is not None:
                    self._thinking.destroy()
                    self._thinking = None
                if kind == "alert":
                    self._append("Alert", text, "alert")
                    messagebox.showwarning("Stock Buddy - Alert!", text)
                else:
                    self._append("Buddy", text, "buddy")
        except queue.Empty:
            pass
        self.root.after(150, self._drain_queue)

    def _update_market_label(self):
        from core.timeutils import market_open
        text, fill = ("Market OPEN - watching drops", self.C["pill_live"]) \
            if market_open() else ("Market closed (opens 9:15am IST)",
                                   self.C["pill"])
        self.market_pill.itemconfig(self.pill_box, fill=fill)
        self.market_pill.itemconfig(self.pill_text, text=text,
                                    fill=self.C["text"])
        self.root.after(60_000, self._update_market_label)

    def _close(self):
        self.app.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
