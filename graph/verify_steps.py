from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from graph.state import GraphState

transformations = standard_transformations + (implicit_multiplication_application,)


def verify_steps_node(state: GraphState) -> GraphState:
    """
    Teacher-mode steps are single statements (narration + display), not
    before/after transformations, so there's no equivalence to check like
    the old solver-mode version did. This does a lighter sanity check:
    if a step is tagged "equation" and has a display value, confirm it's
    at least parseable math. Everything else passes through untouched.
    """
    verified_steps = []
    all_valid = True

    for step in state["steps"]:
        is_valid = True
        if step.get("visual_hint") == "equation" and step.get("display"):
            try:
                expr = step["display"].replace("^", "**")
                expr = expr.replace("+/-", "").replace("±", "")  # sympy can't parse plus-minus notation; strip for parseability check only
                if "=" in expr:
                    left, right = expr.split("=", 1)
                    parse_expr(left.strip(), transformations=transformations)
                    parse_expr(right.strip(), transformations=transformations)
                else:
                    parse_expr(expr.strip(), transformations=transformations)
            except Exception as e:
                is_valid = False
                print(f"  ⚠ Could not parse display for step: '{step['display']}' — {e}")

        step["verified"] = is_valid
        verified_steps.append(step)
        if not is_valid:
            all_valid = False

    print(f"  DEBUG: all_valid = {all_valid}")
    return {**state, "steps": verified_steps, "all_verified": all_valid}