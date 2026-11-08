import tkinter as tk
import time
import math
import random

LYRICS = [
    (0,   "I want one ticket out of your heavy gaze"),
    (4,   "I want one ticket off of your carousel"),
    (9,   "But you should know that I die slow"),
    (13,  "Running through the halls of your haunted home"),
    (18,  "And the toughest part is that we both know"),
    (22,  "What happened to you"),
    (24,  "Why you're out on your own"),
    (26,  "Merry Christmas, please don't call"),
    (31,  "Merry Christmas, I'm not yours at all"),
    (36,  "Merry Christmas, please don't call me"),
    (41,  "Please don't call me"),
    (45,  "Please don't call me"),
    (49,  "Please don't call me"),
]
BOX_W, BOX_H = 240, 150
FONT = ("Helvetica", 15, "bold")
BG_COLOR = "#8A0000"
FG_COLOR = "#FFFFFF"
RISE_SPEED = 50
BOTTOM_SPAWN_OFFSET = 100
TYPEWRITER_DELAY = 65
MUSIC_NOTE_CHARS = ["♪", "♫", "♬", "♩"]
NOTE_FONT_SIZES = [12, 16, 20, 24]
NOTE_COLORS = ["#8A0000", "#A30000", "#B30000", "#C40000"]

NOTE_MIN_SPAWN_GAP = 0.5
NOTE_MAX_SPAWN_GAP = 1.0
NOTE_SPEED_RANGE = (25, 60)
NOTE_WOBBLE_AMP_RANGE = (10, 25)
NOTE_WOBBLE_FREQ_RANGE = (0.8, 1.8)
NOTE_SPAWN_TAIL_BUFFER = 8

class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(
            f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}"
        )
        self.win.resizable(False, False)

        self.full_text = text
        self.x = x
        self.y = float(y)
        self.label = tk.Label(
            self.win,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 30,
            justify="center",
            padx=10,
            pady=10
        )

        self.label.pack(
            expand=True,
            fill="both",
            padx=8,
            pady=8
        )

        self.typewriter_index = 0
        self.typewriter()

    def rise(self, dy):
        self.y -= dy

        self.win.geometry(
            f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}"
        )

    def is_offscreen(self):
        return self.y + BOX_H < -30

    def typewriter(self):
        try:
            if self.typewriter_index <= len(self.full_text):
                self.label.config(
                    text=self.full_text[:self.typewriter_index]
                )

                self.typewriter_index += 1
                self.win.after(TYPEWRITER_DELAY, self.typewriter)

        except tk.TclError:
            pass

    def destroy(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass

class MusicNote:
    def __init__(self, parent, screen_w, screen_h):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-transparentcolor", "#000000")
        except tk.TclError:
            pass

        try:
            self.win.attributes("-alpha", 0.88)
        except tk.TclError:
            pass

        char = random.choice(MUSIC_NOTE_CHARS)
        size = random.choice(NOTE_FONT_SIZES)
        color = random.choice(NOTE_COLORS)

        self.win.configure(bg="#000000")

        self.label = tk.Label(
            self.win,
            text=char,
            font=("Helvetica", size, "bold"),
            bg="#000000",
            fg=color,
            bd=0
        )

        self.label.pack(padx=3, pady=3)
        self.base_x = random.uniform(
            10,
            max(10, screen_w - 50)
        )

        self.y = float(
            screen_h + random.uniform(0, 100)
        )
        self.spawn_time = time.time()
        self.wobble_phase = random.uniform(0, math.tau)

        self.wobble_freq = random.uniform(
            *NOTE_WOBBLE_FREQ_RANGE
        )

        self.wobble_amp = random.uniform(
            *NOTE_WOBBLE_AMP_RANGE
        )

        self.speed = random.uniform(
            *NOTE_SPEED_RANGE
        )

        self._update_pos()

    def _update_pos(self):
        elapsed = time.time() - self.spawn_time

        x = self.base_x + math.sin(
            elapsed * self.wobble_freq + self.wobble_phase
        ) * self.wobble_amp

        self.win.geometry(
            f"+{int(x)}+{int(self.y)}"
        )

    def rise(self, dt):
        self.y -= self.speed * dt
        self._update_pos()

    def is_offscreen(self):
        return self.y < -50

    def destroy(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass

class LyricFloatApp:
    def __init__(self, root):
        self.root = root

        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.notes = []

        self.last_frame_time = None
        self.current_side = "left"

        self.next_note_spawn_time = 0.0

        self.last_lyric_time = (
            LYRICS[-1][0] if LYRICS else 0
        )

        self.start()

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing = BOX_W + 30

        left_x = max(
            10,
            center_x - spacing
        )

        right_x = min(
            self.screen_w - BOX_W - 10,
            center_x + 30
        )

        if self.current_side == "left":
            self.current_side = "right"
            return left_x

        self.current_side = "left"
        return right_x

    def start(self):
        self.root.withdraw()

        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.next_note_spawn_time = self.start_time

        self.tick()

    def _maybe_spawn_note(self, now, elapsed):
        if elapsed > (
            self.last_lyric_time + NOTE_SPAWN_TAIL_BUFFER
        ):
            return

        if now >= self.next_note_spawn_time:
            note = MusicNote(
                self.root,
                self.screen_w,
                self.screen_h
            )

            self.notes.append(note)

            self.next_note_spawn_time = now + random.uniform(
                NOTE_MIN_SPAWN_GAP,
                NOTE_MAX_SPAWN_GAP
            )

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time

        dt = min(
            now - self.last_frame_time,
            0.05
        )

        self.last_frame_time = now
        while (
            self.next_lyric_idx < len(LYRICS)
            and LYRICS[self.next_lyric_idx][0] <= elapsed
        ):
            _, text = LYRICS[self.next_lyric_idx]

            x = self.random_safe_x()

            y = (
                self.screen_h
                - BOX_H
                - BOTTOM_SPAWN_OFFSET
            )

            box = LyricCard(
                self.root,
                text,
                x,
                y
            )

            self.boxes.append(box)
            self.next_lyric_idx += 1
        dy = RISE_SPEED * dt

        for box in self.boxes:
            box.rise(dy)
        visible_boxes = []

        for box in self.boxes:
            if box.is_offscreen():
                box.destroy()
            else:
                visible_boxes.append(box)

        self.boxes = visible_boxes
        self._maybe_spawn_note(now, elapsed)

        for note in self.notes:
            note.rise(dt)
        visible_notes = []

        for note in self.notes:
            if note.is_offscreen():
                note.destroy()
            else:
                visible_notes.append(note)

        self.notes = visible_notes
        if (
            self.next_lyric_idx < len(LYRICS)
            or self.boxes
            or self.notes
        ):
            self.root.after(16, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
