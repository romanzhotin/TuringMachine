from collections import defaultdict
from enum import Enum, auto


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    STAY = auto()


class TuringTape:
    def __init__(self, input_str: str = "", blank_symbol: str = "_"):
        self.blank = blank_symbol
        self.tape = defaultdict(lambda: self.blank)

        for i, ch in enumerate(input_str):
            self.tape[i] = ch

        self.head = 0

    def read(self) -> str:
        return self.tape[self.head]

    def write(self, symbol: str):
        self.tape[self.head] = symbol

    def move(self, direction: Direction, steps: int = 1):
        if direction == Direction.LEFT:
            self.head -= steps
        elif direction == Direction.RIGHT:
            self.head += steps

    def get_tape_snapshot(self, window: int = 10) -> str:
        min_idx = self.head - window
        max_idx = self.head + window
        chars = []
        for pos in range(min_idx, max_idx + 1):
            c = self.tape[pos]
            if pos == self.head:
                chars.append(f"[{c}]")
            else:
                chars.append(f"{c}")
        return " ".join(chars)

    def __str__(self):
        # компактное отображение: от минимально заполненной до максимальной
        if not self.tape:
            return ""
        used_positions = [p for p, s in self.tape.items() if s != self.blank]
        if not used_positions:
            return ""
        lo, hi = min(used_positions), max(used_positions)
        return "".join(self.tape[i] for i in range(lo, hi + 1))

    def reset(self, input_str: str = ""):
        self.tape.clear()
        for i, ch in enumerate(input_str):
            self.tape[i] = ch
        self.head = 0
