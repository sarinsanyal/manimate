import sympy
from sympy import Eq, solve, symbols
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from graph.state import GraphState

transformations = standard_transformations + (implicit_multiplication_application,)


def parse_equation(expr_str: str):
    """Turn a string like '2x + 3 = 7' into a sympy Eq object."""
    left, right = expr_str.split("=")
    x = symbols("x")
    left_expr = parse_expr(left.strip().replace("^", "**"), local_dict={"x": x}, transformations=transformations)
    right_expr = parse_expr(right.strip().replace("^", "**"), local_dict={"x": x}, transformations=transformations)
    return Eq(left_expr, right_expr)


def verify_step(from_expr: str, to_expr: str) -> bool:
    """Check that from_expr and to_expr have the same solution for x."""
    try:
        eq1 = parse_equation(from_expr)
        eq2 = parse_equation(to_expr)
        x = symbols("x")
        sol1 = solve(eq1, x)
        sol2 = solve(eq2, x)
        return sol1 == sol2
    except Exception as e:
        print(f"  Verification error on '{from_expr}' -> '{to_expr}': {e}")
        return False


def verify_steps_node(state: GraphState) -> GraphState:
    verified_steps = []
    all_valid = True

    for step in state["steps"]:
        is_valid = verify_step(step["from_expr"], step["to_expr"])
        step["verified"] = is_valid
        verified_steps.append(step)
        if not is_valid:
            all_valid = False
            print(f"  ⚠ Step failed verification: {step['from_expr']} -> {step['to_expr']}")

    return {**state, "steps": verified_steps, "all_verified": all_valid}