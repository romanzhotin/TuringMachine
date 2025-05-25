from typing import Dict, Set, Tuple
from core.tape import TuringTape, Direction

class TuringMachine:
    def __init__(
            self,
            initial_state: str,
            final_states: Set[str],
            transition_table: Dict[Tuple[str, str], Tuple[str, Direction, str]],
            tape: TuringTape,
            alphabet: Set[str],
            max_steps: int = 1000
    ):
        self.tape = tape
        self.current_state = initial_state
        self.final_states = final_states
        self.transition_table = transition_table
        self.alphabet = alphabet
        self.max_steps = max_steps
        self.is_halted = False
        self.error_occurred = False
        self.error_message = ""
        self.steps_done = 0
        self.trace = []

    def step(self) -> bool:
        if self.is_halted:
            return False

        current_symbol = self.tape.read()
        transition_key = (self.current_state, current_symbol)

        if transition_key not in self.transition_table:
            self.is_halted = True
            self.error_occurred = True
            self.error_message = (
                "Ошибка выполнения!\n"
                f"Для состояния '{self.current_state}' и символа '{current_symbol}' "
                "не найдено правило перехода в таблице."
            )
            return False

        new_symbol, direction, new_state = self.transition_table[transition_key]
        self.trace.append((self.current_state, current_symbol, new_symbol, direction, new_state))

        self.tape.write(new_symbol)
        self.tape.move(direction)
        self.current_state = new_state

        self.steps_done += 1

        if self.current_state in self.final_states:
            self.is_halted = True
        return True

    def run(self) -> None:
        while not self.is_halted and self.steps_done < self.max_steps:
            self.step()

        if not self.is_halted and self.steps_done >= self.max_steps:
            self.is_halted = True
            self.error_occurred = True
            self.error_message = f"Превышено максимальное число шагов ({self.max_steps})."

    def get_tape_snapshot(self, window: int = 10) -> str:
        return self.tape.get_tape_snapshot(window)

    def get_current_state(self) -> str:
        return self.current_state

    def get_tape_output(self) -> str:
        return str(self.tape)
