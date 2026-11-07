import ast
import operator

from app.tools.base_tool import BaseTool


MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 1000
MAX_INT_BITS = 4096


class CalculatorTool(BaseTool):

    def __init__(self):
        super().__init__("Calculator")

        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

    def execute(self, expression):
        """
        Safely evaluate a mathematical expression.
        """

        try:
            expression = self._extract_expression(expression)

            if len(expression) > MAX_EXPRESSION_LENGTH:
                raise ValueError("Expression is too long.")

            tree = ast.parse(expression, mode="eval")
            return self._evaluate(tree.body)

        except Exception as exc:
            raise ValueError(
                f"Invalid mathematical expression: {expression}"
            ) from exc

    def _extract_expression(self, expression):
        """
        Extract the mathematical expression from a natural-language request.
        """

        expression = expression.strip()

        prefixes = [
            "calculate",
            "what is",
            "what's",
            "can you calculate",
            "please calculate",
        ]

        lowered = expression.lower()

        for prefix in prefixes:

            if lowered.startswith(prefix):
                expression = expression[len(prefix):].strip()
                break

        expression = expression.rstrip("?.!")

        return expression.strip()
    
    def _evaluate(self, node):

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Only numbers are allowed.")

        if isinstance(node, ast.BinOp):
            operation = self.operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
                raise ValueError("Exponent is too large.")

            result = operation(left, right)

            if isinstance(result, int) and result.bit_length() > MAX_INT_BITS:
                raise ValueError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp):
            operation = self.operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported unary operator.")

            operand = self._evaluate(node.operand)

            return operation(operand)

        raise ValueError(
            "Only mathematical expressions are supported."
        )