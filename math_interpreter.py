import ast
import operator as op


class MathInterpreter:

    __operators_map = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.USub: op.neg,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
    }

    @staticmethod
    def eval(expression: str, variables: dict[str, int | float]) -> int | float:
        root_node = ast.parse(expression, mode='eval')
        return MathInterpreter.__walk(root_node, variables)

    @staticmethod
    def __walk(node: ast.AST, variables: dict[str, int | float]) -> int | float:
        match node:
            case ast.Expression():
                return MathInterpreter.__walk(node.body, variables)
            case ast.Num():
                return node.n
            case ast.BinOp():
                left, right, op = node.left, node.right, node.op
                method = MathInterpreter.__operators_map[type(op)]
                return method(MathInterpreter.__walk(left, variables), MathInterpreter.__walk(right, variables))
            case ast.UnaryOp():
                operand, op = node.operand, node.op
                method = MathInterpreter.__operators_map[type(op)]
                return method(MathInterpreter.__walk(operand, variables))
            case ast.Name():
                id = node.id
                return variables[id]
            case _:
                raise TypeError()


def main():
    print(MathInterpreter.eval("a - l", {"a":2, "l":4}))

if __name__ == "__main__":
    main()
