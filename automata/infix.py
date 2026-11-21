"""NPDA recognizer for infix expressions using the CFG agreed in the design.

Stack convention: index 0 is the TOP of stack (top is on the left).
The PDA has one processing state q1 with a self-loop for CFG expansion
and terminal matching.
"""

from collections import deque
from string import digits

NONTERMINALS = {"E", "E'", "T", "T'", "F"}
TERMINALS = set(digits) | set("+-*/()")
Z0 = "Z0"

PRODUCTIONS = {
    "E": [["T", "E'"]],
    "E'": [["+", "T", "E'"], ["-", "T", "E'"], []],
    "T": [["F", "T'"]],
    "T'": [["*", "F", "T'"], ["/", "F", "T'"], []],
    "F": [["(", "E", ")"]] + [[digit] for digit in digits],
}


def normalize_expression(expression: str) -> str:
    """Remove whitespace while preserving all expression symbols."""
    return "".join(expression.split())


def _remaining_text(source, index):
    remaining = source[index:]
    return remaining if remaining else "ε"


def recognize_infix(expression: str, max_configurations: int = 100_000):
    """Recognize an infix expression and return (accepted, transition_log, message)."""
    source = normalize_expression(expression)

    if not source:
        return False, [], "Ekspresi tidak boleh kosong."

    invalid = sorted(set(source) - TERMINALS)
    if invalid:
        return False, [], f"Karakter tidak valid: {', '.join(invalid)}"

    # q0 initializes the stack; q1 is the only processing state.
    log = [{
        "step": 0,
        "state": "q0",
        "input_read": "ε",
        "action": "Inisialisasi: ε, Z0 → E Z0",
        "stack": ["E", Z0],
        "remaining": source,
    }]

    # BFS ensures we find an accepting derivation without getting trapped
    # in an unsuccessful nondeterministic branch.
    start = (0, ("E", Z0))
    queue = deque([(start, [])])
    visited = {start}
    explored = 0
    successful_path = None

    while queue and explored < max_configurations:
        (index, stack), path = queue.popleft()
        explored += 1

        if index == len(source) and stack == (Z0,):
            successful_path = path
            break

        if not stack:
            continue

        top = stack[0]
        rest = stack[1:]

        # CFG expansion: ε, Nonterminal → RHS (all remain in q1).
        if top in NONTERMINALS:
            # The grammar is LL(1), so use the next input symbol to select
            # the applicable production. This avoids exploring impossible
            # epsilon-expansion branches for malformed expressions.
            lookahead = source[index] if index < len(source) else "$"
            if top == "E":
                choices = [["T", "E'"]]
            elif top == "T":
                choices = [["F", "T'"]]
            elif top == "E'":
                if lookahead == "+":
                    choices = [["+", "T", "E'"]]
                elif lookahead == "-":
                    choices = [["-", "T", "E'"]]
                elif lookahead in {")", "$"}:
                    choices = [[]]
                else:
                    choices = []
            elif top == "T'":
                if lookahead == "*":
                    choices = [["*", "F", "T'"]]
                elif lookahead == "/":
                    choices = ["/", "F", "T'"]
                    choices = [choices]
                elif lookahead in {"+", "-", ")", "$"}:
                    choices = [[]]
                else:
                    choices = []
            else:  # F
                if lookahead == "(":
                    choices = [["(", "E", ")"]]
                elif lookahead in digits:
                    choices = [[lookahead]]
                else:
                    choices = []

            for rhs in choices:
                new_stack = tuple(rhs) + rest
                rhs_text = " ".join(rhs) if rhs else "ε"
                action = f"Ekspansi {top} → {rhs_text}"
                config = (index, new_stack)
                if config not in visited:
                    visited.add(config)
                    new_entry = {
                        "state": "q1",
                        "input_read": "ε",
                        "action": action,
                        "stack": list(new_stack),
                        "remaining": _remaining_text(source, index)
                    }
                    queue.append((config, path + [new_entry]))

        # Terminal matching: a, a → ε (consume input and pop stack).
        elif top in TERMINALS and index < len(source) and source[index] == top:
            new_stack = tuple(rest)
            config = (index + 1, new_stack)
            action = f"Cocokkan '{top}': {top}, {top} → ε"
            if config not in visited:
                visited.add(config)
                new_entry = {
                    "state": "q1",
                    "input_read": top,
                    "action": action,
                    "stack": list(new_stack) if new_stack else ["ε"],
                    "remaining": _remaining_text(source, index + 1)
                }
                queue.append((config, path + [new_entry]))

    if successful_path is None:
        if explored >= max_configurations:
            message = "Batas pencarian konfigurasi tercapai."
        else:
            message = "Ekspresi ditolak: tidak ada jalur PDA yang dapat mencocokkan seluruh input."
        return False, log, message

    for number, entry in enumerate(successful_path, start=1):
        entry["step"] = number
        log.append(entry)

    log.append({
        "step": len(log),
        "state": "q1",
        "input_read": "ε",
        "action": "Final check: ε, Z0 → Z0; input habis, pindah ke qf",
        "stack": [Z0],
        "remaining": "ε",
    })
    log.append({
        "step": len(log),
        "state": "qf",
        "input_read": "ε",
        "action": "Ekspresi diterima (accept)",
        "stack": [Z0],
        "remaining": "ε",
    })
    return True, log, "Ekspresi infix diterima oleh PDA."


def get_infix_transitions():
    """Human-readable transition summary for the UI."""
    return [
        ("q0", "ε", "Z0", "E Z0", "q1", "Inisialisasi stack"),
        ("q1", "ε", "E", "T E'", "q1", "Produksi E"),
        ("q1", "ε", "E'", "+ T E' | - T E' | ε", "q1", "Produksi E'"),
        ("q1", "ε", "T", "F T'", "q1", "Produksi T"),
        ("q1", "ε", "T'", "* F T' | / F T' | ε", "q1", "Produksi T'"),
        ("q1", "ε", "F", "( E ) | A | B | ... | Z", "q1", "Produksi F"),
        ("q1", "ε", "F", "( E ) | 0 | 1 | ... | 9", "q1", "Operand berupa angka 0 sampai 9"),
        ("q1", "a", "a", "ε", "q1", "Matching terminal; a ∈ 0-9, +, -, *, /, (, )"),
    ]
