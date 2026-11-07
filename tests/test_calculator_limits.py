import time
import unittest

from app.tools.calculator_tool import CalculatorTool


class CalculatorLimits(unittest.TestCase):
    def setUp(self):
        self.calc = CalculatorTool()

    def test_normal_math_still_works(self):
        self.assertEqual(self.calc.execute("2 + 3 * 4"), 14)
        self.assertEqual(self.calc.execute("what is 10 / 4?"), 2.5)
        self.assertEqual(self.calc.execute("calculate 2 ** 10"), 1024)
        self.assertEqual(self.calc.execute("-(3 + 2)"), -5)

    def test_huge_power_is_rejected_quickly(self):
        for expr in ("9 ** 9 ** 9 ** 9", "2 ** 100000", "10 ** 1001"):
            started = time.perf_counter()
            with self.assertRaises(ValueError, msg=expr):
                self.calc.execute(expr)
            self.assertLess(time.perf_counter() - started, 1.0, expr)

    def test_huge_multiplication_result_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calc.execute("(10 ** 1000) * (10 ** 1000) * (10 ** 1000) * (10 ** 1000)")

    def test_overlong_expression_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calc.execute("1+" * 150 + "1")

    def test_code_injection_is_rejected(self):
        for expr in ("__import__('os').system('echo hi')", "open('x')", "[1,2][0]", "lambda: 1"):
            with self.assertRaises(ValueError, msg=expr):
                self.calc.execute(expr)

    def test_division_by_zero_is_a_value_error(self):
        with self.assertRaises(ValueError):
            self.calc.execute("1 / 0")


if __name__ == "__main__":
    unittest.main()
