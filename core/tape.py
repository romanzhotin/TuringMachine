from enum import Enum, auto


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    STAY = auto()


class TuringTape:
    def __init__(self, input_str: str = "", blank_symbol: str = " "):
        self.blank = blank_symbol
        self.tape = {}
        for i, ch in enumerate(input_str):
            if ch != self.blank:
                self.tape[i] = ch
        self.head = 0
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def _notify_observers(self):
        for observer in self._observers:
            observer.on_tape_changed()

    def read(self) -> str:
        return self.tape.get(self.head, self.blank)

    def write(self, symbol: str):
        if symbol == self.blank:
            self.tape.pop(self.head, None)
        else:
            self.tape[self.head] = symbol
        self._notify_observers()

    def move(self, direction: Direction, steps: int = 1):
        if direction == Direction.LEFT:
            self.head -= steps
        elif direction == Direction.RIGHT:
            self.head += steps
        self._notify_observers()

    def get_tape_snapshot(self, window: int = 10) -> str:
        min_idx = self.head - window
        max_idx = self.head + window
        chars = []
        for pos in range(min_idx, max_idx + 1):
            c = self.tape.get(pos, self.blank)
            if pos == self.head:
                chars.append(f"[{c}]")
            else:
                chars.append(f"{c}")
        return " ".join(chars)

    def __str__(self):
        if not self.tape:
            return ""
        lo, hi = min(self.tape), max(self.tape)
        return "".join(self.tape.get(i, self.blank) for i in range(lo, hi + 1))

    def reset(self, input_str: str = ""):
        self.tape.clear()
        for i, ch in enumerate(input_str):
            if ch != self.blank:
                self.tape[i] = ch
        self.head = 0

    def set_symbol(self, pos: int, symbol: str):
        if symbol == self.blank:
            self.tape.pop(pos, None)
        else:
            self.tape[pos] = symbol
        self._notify_observers()
