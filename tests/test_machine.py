import unittest
from core.machine import TuringMachine, Direction
from core.tape import TuringTape


class TestTuringMachine(unittest.TestCase):
    def setUp(self):
        self.states = {"q0", "q_accept"}
        self.input_alphabet = {"a", "b"}
        self.tape_alphabet = {"a", "b", "_"}
        self.blank = "_"
        self.start = "q0"
        self.accept = {"q_accept"}

    def test_run_simple(self):
        transitions = {
            ('q0', 'a'): ('q0', 'b', Direction.RIGHT),
            ('q0', 'b'): ('q0', 'a', Direction.RIGHT),
            ('q0', '_'): ('q_accept', '_', Direction.STAY)
        }
        tape = TuringTape("ab", self.blank)
        machine = TuringMachine(tape, self.states, self.input_alphabet,
                                self.tape_alphabet, self.blank, self.start,
                                self.accept, transitions)
        result = machine.run()
        self.assertTrue(result)
        self.assertEqual(tape.tape[0], 'b')
        self.assertEqual(tape.tape[1], 'a')

    def test_halt_without_accept(self):
        transitions = {
            ('q0', 'a'): ('q0', 'a', Direction.RIGHT)
        }
        tape = TuringTape("a", self.blank)
        machine = TuringMachine(tape, self.states, self.input_alphabet,
                                self.tape_alphabet, self.blank, self.start,
                                self.accept, transitions, max_steps=5)
        result = machine.run()
        self.assertFalse(result)

    def test_load_save_json(self):
        transitions = {
            ('q0', 'a'): ('q0', 'b', Direction.RIGHT),
            ('q0', 'b'): ('q0', 'a', Direction.RIGHT),
            ('q0', '_'): ('q_accept', '_', Diretion.STAY)
        }
        tape = TuringTape("ab", self.blank)
        machine = TuringMachine(tape, self.states, self.input_alphabet,
                                self.tape_alphabet, self.blank, self.start,
                                self.accept, transitions)
        json_data = machine.save_to_json()
        new_machine = TuringMachine.load_from_json(json_data)
        self.assertEqual(machine.states, new_machine.states)
        self.assertEqual(machine.transitions, new_machine.transitions)


if __name__ == '__main__':
    unittest.main()
