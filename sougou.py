from __future__ import annotations

import os
import random
import tkinter as tk
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageTk
from typing_extensions import Self


def load_image(path: Path) -> Image.Image:
    with path.open("rb") as f:
        image = Image.open(f)
        image.load()
    return image


GAME_WINDOW_WIDTH = 500
GAME_WINDOW_HEIGHT = 800

SCORE_BOARD_HEIGHT = 50

ROSE_SIZES = [30, 60, 120]
ROSE_SCORES = [10, 20, 30]
ROSE_PATH = Path() / "images" / "bara.jpg"
BG_PATH = Path() / "images" / "wood.jpg"

LOSE_IMAGE = load_image(ROSE_PATH)
BG_IMAGE = load_image(BG_PATH)


class Root:
    flower_per_sec: float = 1.0
    time_limit_sec: int = 10
    interval_ms: int = 10

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(
            f"{GAME_WINDOW_WIDTH}x{GAME_WINDOW_HEIGHT + SCORE_BOARD_HEIGHT}"
        )
        self.score_board = ScoreBoard(self.root, self.time_limit_sec)
        self.game = RoseBoard(self.root, add_score=self.add_score)
        self.elapsed_time_ms = 0
        self.score = 0

    def start(self):
        self.gen_flower_loop()
        self.root.mainloop()

    def is_cleared(self):
        return self.elapsed_time_ms / 1000 >= self.time_limit_sec

    def gen_flower_loop(self):
        if self.is_cleared():
            return
        self.clock()
        if random.random() < self.flower_per_sec * self.interval_ms / 1000.0:
            self.game.gen_random_rose()
        self.root.after(self.interval_ms, self.gen_flower_loop)

    def clock(self):
        self.elapsed_time_ms += self.interval_ms
        self.score_board.set_elapsed_time(self.elapsed_time_ms)
        self.score_board.update()

    def add_score(self, additional_score: int):
        self.score += additional_score
        self.score_board.set_score(self.score)


class ScoreBoard:
    def __init__(self, master: tk.Misc, time_limit_sec: int):
        self.window = tk.Frame(
            master,
            width=GAME_WINDOW_WIDTH,
            height=SCORE_BOARD_HEIGHT,
        )
        self.time_limit_sec = time_limit_sec
        self.score = 0
        self.text = tk.StringVar(self.window)
        self.label = tk.Label(master, textvariable=self.text, height=2)
        self.label.pack()

        self.set_elapsed_time(0)
        self.set_score(0)

    def set_elapsed_time(self, elapsed_time_ms: int):
        remain = self.time_limit_sec - elapsed_time_ms / 1000
        self.time_text = f"Time: {int(remain)}:{int((remain - int(remain)) * 100)}"

    def set_score(self, score: int):
        self.score_text = f"Score: {score}"

    def update(self):
        text = f"{self.time_text}{os.linesep}{self.score_text}"
        self.text.set(text)


class RoseBoard:
    num_click: int = 5

    def __init__(self, master: tk.Misc, add_score: Callable[[int], None]):
        self.roses: dict[str, RoseButton] = {}
        self.add_score = add_score

        self.window = tk.Frame(
            master, height=GAME_WINDOW_HEIGHT, width=GAME_WINDOW_WIDTH
        )
        self.window.pack()

        self.draw_bg()

    def draw_bg(self):
        self.bg_image = ImageTk.PhotoImage(
            BG_IMAGE.resize((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT))
        )
        self.bg_label = tk.Label(self.window, image=self.bg_image)
        self.bg_label.pack()

    def register_rose(self, rose: RoseButton):
        idx = str(uuid.uuid4())
        self.roses[idx] = rose

        def on_click(_event):
            nonlocal rose
            rose.count_down()
            if rose.counter == 0:
                rose.button.destroy()
                self.roses.pop(idx)
                self.add_score(rose.score)

        rose.bind(on_click)

    def gen_random_rose(self):
        size_idx = random.choice([0, 1, 2])
        rose_size = ROSE_SIZES[size_idx]
        score = ROSE_SCORES[size_idx]

        x_max = GAME_WINDOW_WIDTH - rose_size
        y_max = GAME_WINDOW_HEIGHT - rose_size
        x = int(random.random() * x_max)
        y = int(random.random() * y_max)
        rose = RoseButton.with_master(self.window, self.num_click, rose_size, score)
        rose.place(x, y)
        self.register_rose(rose)


@dataclass
class RoseButton:
    tk_image: ImageTk.PhotoImage
    button: tk.Button
    counter: int
    score: int
    LEFT_CLICK: str = "<Button-1>"

    @classmethod
    def with_master(
        cls, master: tk.Misc, num_click: int, size: int, score: int
    ) -> Self:
        tk_image = ImageTk.PhotoImage(LOSE_IMAGE.resize((size, size)))
        button = tk.Button(master=master, image=tk_image)
        return cls(tk_image, button, num_click, score)

    def place(self, x: int, y: int):
        self.button.place(x=x, y=y)

    def bind(self, func: Callable):
        self.button.bind(self.LEFT_CLICK, func)

    def count_down(self):
        self.counter -= 1


if __name__ == "__main__":
    root = Root()
    root.start()
