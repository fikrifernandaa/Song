import tkinter as tk
import time

LYRICS = [
    (0, "It's over, it's over, oh yeah"),
    (2, "This ain't the first time"),
    (3.5, "I've been hostage to these tears"),
    (6, "I can't believe I'm finally"),
    (8, "moving through my fears"),
    (11, "At least I know how hard"),
    (12.5, "we tried, both you and me"),
    (15, "Didn't we? Didn't we?")
]

BOX_W, BOX_H = 240, 150

FONT = ("Helvetica", 15, "bold")

BG_COLOR = "#FFFFFF"
FG_COLOR = "#111111"

RISE_SPEED = 100
BOTTOM_SPAWN_OFFSET = 0
GAP = 25

TYPEWRITER_DELAY = 50
FLIP_INTERVAL = 300

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
        self.typewriter_index = 0
        self.flip_state = False

        self.label = tk.Label(
            self.win,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 30,
            justify="center"
        )

        self.label.pack(
            expand=True,
            fill="both",
            padx=12,
            pady=12
        )

        self.typewriter()
    def typewriter(self):
        try:
            if self.typewriter_index <= len(self.full_text):
                self.label.config(
                    text=self.full_text[:self.typewriter_index]
                )

                self.typewriter_index += 1

                self.win.after(
                    TYPEWRITER_DELAY,
                    self.typewriter
                )
        except tk.TclError:
            pass
    def rise(self, dy):
        self.y -= dy

        self.win.geometry(
            f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}"
        )
    def is_offscreen(self):
        return self.y + BOX_H < -20
    def flip(self):
        self.flip_state = not self.flip_state

        if self.flip_state:
            bg = "#111111"
            fg = "#FFFFFF"
        else:
            bg = "#FFFFFF"
            fg = "#111111"

        try:
            self.win.configure(bg=bg)
            self.label.configure(
                bg=bg,
                fg=fg
            )
        except tk.TclError:
            pass
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

        self.current_side = "left"

        self.start_time = None
        self.last_frame_time = None
        self.last_flip_time = 0

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

        self.tick()
    def flip_all(self):
        for box in self.boxes:
            box.flip()
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

            if self.boxes:
                y = self.boxes[-1].y + BOX_H + GAP
            else:
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
        if now - self.last_flip_time >= FLIP_INTERVAL / 1000:
            self.flip_all()
            self.last_flip_time = now
        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
