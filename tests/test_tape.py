import unittest
from core.tape import TuringTape, Direction


class TestTuringTape(unittest.TestCase):
    def test_initialization(self):
        tape = TuringTape("abc", "_")
        self.assertEqual(tape.read(), "a")
        tape.move(Direction.RIGHT)
        self.assertEqual(tape.read(), "b")

    def test_write_and_move(self):
        tape = TuringTape("a", "_")
        tape.write("x")
        self.assertEqual(tape.read(), "x")
        tape.move(Direction.RIGHT)
        self.assertEqual(tape.read(), "_")

    def test_reset(self):
        tape = TuringTape("abc", "_")
        tape.reset("xyz")
        self.assertEqual(tape.read(), "x")

    def test_snapshot(self):
        tape = TuringTape("abc", "_")
        snapshot = tape.get_tape_snapshot(window=2)
        self.assertIn("[a]", snapshot)
        self.assertIn("b", snapshot)


if __name__ == '__main__':
    unittest.main()
