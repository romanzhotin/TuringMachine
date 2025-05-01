from typing import Dict, Tuple, Set, Optional, cast
from core.tape import TuringTape, Direction


Transition = Tuple[str, str, Direction]


class TuringMachine:
    def __init__(
        self,
        tape: TuringTape,
        states: Set[str],
        input_alphabet: Set[str],
        tape_alphabet: Set[str],
        blank_symbol: str,
        start_state: str,
        accept_states: Set[str],
        transitions: Dict[Tuple[str, str], Transition],
        max_steps: Optional[int] = 1000
    ):
        self.tape = tape
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.blank_symbol = blank_symbol
        self.start_state = start_state
        self.current_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions
        self.max_steps = max_steps
        self.step_count = 0

    def reset(self, input_string: Optional[str] = None):
        if input_string is not None:
            self.tape.reset(input_string)
        else:
            self.tape.reset()
        self.current_state = self.start_state
        self.step_count = 0

    def step(self) -> bool:
        symbol = self.tape.read()
        key = (self.current_state, symbol)
        if key not in self.transitions:
            return False

        new_state, write_symbol, direction = self.transitions[key]
        self.tape.write(write_symbol)
        self.current_state = new_state
        self.tape.move(direction)
        self.step_count += 1
        return True

    def run(self) -> bool:
        while True:
            if self.max_steps is not None and self.step_count >= self.max_steps:
                break
            if not self.step():
                break
        return self.current_state in self.accept_states

    @classmethod
    def load_from_json(cls, json_data: dict) -> 'TuringMachine':
        states = set(json_data['states'])
        input_alphabet = set(json_data['input_alphabet'])
        tape_alphabet = set(json_data['tape_alphabet'])
        blank = json_data['blank_symbol']
        start = json_data['start_state']
        accept = set(json_data['accept_states'])
        max_steps = json_data.get('max_steps', 1000)

        # Разбор переходов
        trans: Dict[Tuple[str, str], Transition] = {}
        for key, val in json_data['transitions'].items():
            st, sym = key.split(',')
            new_st, write_sym, dir_str = val  # type: str, str, str
            # Приведение типов для соответствия Transition
            trans[(st, sym)] = cast(Transition, (new_st, write_sym, Direction[dir_str]))

        tape = TuringTape(json_data.get('tape', ''), blank)

        return cls(
            tape, states, input_alphabet, tape_alphabet,
            blank, start, accept, trans, max_steps
        )

    def save_to_json(self) -> dict:
        trans_dict: Dict[str, list] = {}
        for (st, sym), (new_st, write_sym, direction) in self.transitions.items():
            trans_dict[f"{st},{sym}"] = [new_st, write_sym, direction.name]

        return {
            'states': list(self.states),
            'input_alphabet': list(self.input_alphabet),
            'tape_alphabet': list(self.tape_alphabet),
            'blank_symbol': self.blank_symbol,
            'start_state': self.start_state,
            'accept_states': list(self.accept_states),
            'transitions': trans_dict,
            'tape': str(self.tape),
            'max_steps': self.max_steps
        }
