"""PDA-style recognizer for postfix expressions.

Stack convention: the rightmost item is the TOP of stack.
X = one operand; Y = a result produced by applying an operator.
"""

import string

OPERANDS = set("0123456789")
OPERATORS = set("+-*/")


def recognize_postfix(expression: str):
    source = "".join(expression.split())
    if not source:
        return False, [], "Ekspresi tidak boleh kosong."

    invalid = sorted(set(source) - OPERANDS - OPERATORS)
    if invalid:
        return False, [], f"Karakter tidak valid: {', '.join(invalid)}"

    stack = ["Z0"]
    state = "q0"
    log = []

    def record(action, input_read, remaining):
        log.append({
            "step": len(log),
            "state": state,
            "input_read": input_read,
            "action": action,
            "stack": stack.copy(),
            "remaining": remaining,
        })

    record("Inisialisasi stack dengan Z0", "ε", source + "$")

    # q1 reads the first operand only.
    first = source[0]
    if first not in OPERANDS:
        return False, log, "Postfix harus diawali operand."
    state = "q1"
    stack.append("X")
    record(f"Baca operand pertama '{first}': push X", first, source[1:] + "$")
    state = "q2"

    for index, symbol in enumerate(source[1:], start=1):
        remaining = source[index + 1:] + "$"
        if symbol in OPERANDS:
            stack.append("X")
            record(f"Baca operand '{symbol}': push X", symbol, remaining)
        elif symbol in OPERATORS:
            # q2 -> q3: consume operator and pop first item
            if len(stack) <= 1 or stack[-1] not in {"X", "Y"}:
                return False, log, f"Operator '{symbol}' tidak memiliki dua operand yang cukup."
            state = "q2"
            stack.pop()
            record(f"Baca operator '{symbol}', POP operand pertama", symbol, remaining)

            # q3 -> q4: epsilon-pop second item
            if len(stack) <= 1 or stack[-1] not in {"X", "Y"}:
                return False, log, f"Operator '{symbol}' tidak memiliki dua operand yang cukup."
            state = "q3"
            stack.pop()
            record("POP operand kedua", "ε", remaining)

            # q4 -> q2: push result Y
            state = "q4"
            stack.append("Y")
            record("PUSH hasil operasi Y; kembali ke q2", "ε", remaining)
            state = "q2"

    # Internal end marker: accept only if exactly one computed item remains.
    if len(stack) != 2 or stack[-1] not in {"X", "Y"}:
        return False, log, "Postfix ditolak: setelah input habis harus tersisa tepat satu hasil."

    state = "q2"
    stack.pop()
    record("Baca penanda akhir '$': POP hasil terakhir", "$", "ε")
    state = "q5"
    if stack != ["Z0"]:
        return False, log, "Postfix ditolak: stack tidak kembali ke Z0."
    stack.pop()
    record("POP Z0; menuju qf", "ε", "ε")
    state = "qf"
    return True, log, "Ekspresi postfix diterima oleh PDA."
