import unittest
from core.tape import TuringTape, Direction
from core.machine import TuringMachine


class TestTuringMachine(unittest.TestCase):
    def test_basic_transition(self):
        tape = TuringTape('A')
        transitions = {
            ('Start', 'A'): ('B', Direction.RIGHT, 'NextState')
        }

        tm = TuringMachine(
            initial_state='Start',
            final_states={'Halt'},
            transition_table=transitions,
            tape=tape,
            alphabet={'A', 'B', '_'}
        )

        self.assertEqual(tm.get_current_state(), 'Start')
        self.assertEqual(tape.read(), 'A')

        result = tm.step()

        self.assertTrue(result)
        self.assertEqual(tm.get_current_state(), 'NextState')
        self.assertEqual(str(tape), 'B')
        self.assertEqual(tape.read(), '_')

    def test_final_state_halting(self):
        tape = TuringTape('X')
        transitions = {
            ('Init', 'X'): ('Y', Direction.LEFT, 'HALT')
        }

        tm = TuringMachine(
            initial_state='Init',
            final_states={'HALT'},
            transition_table=transitions,
            tape=tape,
            alphabet={'X', 'Y', '_'}
        )

        tm.step()
        self.assertTrue(tm.is_halted)
        self.assertEqual(tm.get_current_state(), 'HALT')
        self.assertEqual(str(tape), 'Y')

    def test_no_transition_halting(self):
        tape = TuringTape('0')
        tm = TuringMachine(
            initial_state='Unknown',
            final_states={'End'},
            transition_table={},
            tape=tape,
            alphabet={'0', '1', '_'}
        )

        result = tm.step()
        self.assertFalse(result)
        self.assertTrue(tm.is_halted)
        self.assertEqual(tm.get_current_state(), 'Unknown')


if __name__ == '__main__':
    unittest.main()
