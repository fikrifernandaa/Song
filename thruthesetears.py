import time
import sys

lyrics = [

    ("You said it was over", 0.15, 0.6),
    ("But when we got closer", 0.15, 0.5),
    ("You cried on my shoulder", 0.15, 0.5),
    ("Goodbye", 0.15, 1.95),
    ("", 0, 2.2),

    ("In the end, I'm gonna be alright", 0.1, 0.9),
    ("But it might take a hundred sleepless nights", 0.07, 0.8),
    ("To make the memories of you disappear", 0.07, 1.2),
    ("But right now, I can't see nothing through these tears", 0.06, 0.9),
    ("", 0, 0.1),

    ("Out of sight but you're not out of my mind", 0.09, 0.46),
    ("So it might take somebody else at night", 0.088, 0.47),
    ("To make it feel like you were never here", 0.088, 0.40),
    ("But right now, I can't see nothing through these tears ", 0.063, 1.22),
]


def ketik(teks, delay):
    for huruf in teks:
        sys.stdout.write(huruf)
        sys.stdout.flush()
        time.sleep(delay)
    print()


for teks, delay, jeda in lyrics:
    ketik(teks, delay)
    time.sleep(jeda)