import numpy as np
from typing import List, Dict, Tuple
from pprint import pprint

PROGRAM = '''
PROCEDURE MoveLeftAndUp
LEFT 2
UP 2
ENDPROC

SET X = 4
REPEAT X
IFBLOCK RIGHT
REPEAT 3
CALL MoveLeftAndUp
ENDREPEAT
ENDIF
ENDREPEAT


'''

N = 21


class C:
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    UP = "UP"
    DOWN = "DOWN"
    IFBLOCK = "IFBLOCK"
    ENDIF = "ENDIF"
    REPEAT = "REPEAT"
    ENDREPEAT = "ENDREPEAT"
    SET = "SET"
    PROCEDURE = "PROCEDURE"
    ENDPROC = "ENDPROC"
    CALL = "CALL"
    JMP = "JMP"
    MOV = "MOV"


def print_code_lines(code_lines: List[List[str]]):
    for idx, line in enumerate(code_lines):
        print(f'{idx:<2} {line}')


def initial_preparations(code: str) -> List[List[str]]:
    return list(filter(lambda l: len(l) > 0, map(lambda s: s.strip().split(), code.strip().splitlines())))


def check_n(var: str, digit_required=False) -> bool:
    if var.isdigit():
        return 1 <= int(var) <= 1000
    else:
        return not digit_required and not var[0].isdigit()


def check_command_syntax(code_lines: List[List[str]]) -> str:
    for idx, line in enumerate(code_lines):
        match line[0]:
            case C.RIGHT | C.LEFT | C.UP | C.DOWN | C.REPEAT:
                if len(line) == 2 and check_n(line[1]):
                    continue
            case C.PROCEDURE | C.CALL:
                if len(line) == 2 and not line[1][0].isdigit():
                    continue
            case C.IFBLOCK:
                if len(line) == 2 and line[1] in [C.RIGHT, C.LEFT, C.UP, C.DOWN]:
                    continue
            case C.SET:
                if len(line) < 4:
                    sep = "".join(line[1:]).split('=')
                    if len(sep) == 2:
                        line = [C.SET, sep[0], '=', sep[1]]

                if len(line) == 4 and not line[1][0].isdigit() and line[2] == '=' and check_n(line[3], True):
                    line.pop(2)
                    code_lines[idx] = line
                    continue
            case C.ENDIF | C.ENDREPEAT | C.ENDPROC:
                if len(line) == 1:
                    continue
            case _:
                ...

        return ' '.join(line)
    return ''


def check_variable_declaration_and_replace_consts(code_lines: List[List[str]]) -> str:
    variables = {}
    for idx, line in enumerate(code_lines):
        if line[0] == C.SET:
            variables[line[1]] = line[2]
        elif line[0] in [C.RIGHT, C.LEFT, C.UP, C.DOWN, C.REPEAT] and not line[1].isdigit():
            if val := variables.get(line[1]):
                code_lines[idx][1] = val
            else:
                return f'Usage undefined variable "{" ".join(line)}"'

    return ''


def check_procedure_declaration_and_replace_procedures(code_lines: List[List[str]]) -> str:
    procedures = {}

    start = -1
    for idx, line in enumerate(code_lines):
        if line[0] == C.PROCEDURE:
            if line[1] in procedures:
                return f'Redeclaration procedure "{" ".join(line)}"'
            start = idx
        elif line[0] == C.CALL:
            if val := procedures.get(line[1]):
                code_lines[val[0]] = ["JUMP", val[1] + 1]
                code_lines[val[1]] = ["JUMP", idx + 1]
                code_lines[idx] = ["JUMP", val[0] + 1]
            else:
                return f'Call undefined procedure "{" ".join(line)}"'
        elif line[0] == C.ENDPROC:
            procedures[code_lines[start][1]] = start, idx

    return ''


def check_code_nesting(code_lines: List[List[str]], blocks: List[Tuple[int, int]]) -> str:
    alias = {
        C.IFBLOCK: 1,
        C.ENDIF: -1,
        C.REPEAT: 2,
        C.ENDREPEAT: -2,
        C.PROCEDURE: 3,
        C.ENDPROC: -3
    }

    stack = []
    max_nesting = 0
    cur_nesting = 0
    for idx, line in enumerate(code_lines):
        if val := alias.get(line[0]):
            if val > 0:
                if cur_nesting > 0 and line[0] == C.PROCEDURE:
                    return f"Procedure declaration in block {' '.join(line)}"
                stack.append((val, idx))
                cur_nesting += 1
                max_nesting = max(max_nesting, cur_nesting)
            else:
                if len(stack) > 0 and (start := stack.pop())[0] == -val:
                    if code_lines[start[1]][0] != C.PROCEDURE:
                        blocks.append((start[1], idx))
                    cur_nesting -= 1
                else:
                    return ' '.join(line)

    if len(stack) != 0:
        return "Construction not closed"

    if max_nesting > 3:
        return f'Max nesting limit exceeded "{max_nesting}"'

    return ''


def bytecode_compile(code_lines: List[List[str]], blocks: List[Tuple[int, int]]) -> List[List[str]]:
    bytecode_lines: List[List[str]] = []
    for line in code_lines:
        ...

    return bytecode_lines


def main():
    code_lines = initial_preparations(PROGRAM)

    if error := check_command_syntax(code_lines):
        return print(f'Syntax error: {error}')

    if error := check_variable_declaration_and_replace_consts(code_lines):
        return print(f'Variable declaration error: {error}')

    if error := check_procedure_declaration_and_replace_procedures(code_lines):
        return print(f'Procedure declaration error: {error}')

    blocks: List[Tuple[int, int]] = []
    if error := check_code_nesting(code_lines, blocks):
        return print(f'Nesting error: {error}')

    bytecode_lines = bytecode_compile(code_lines, blocks)
    print_code_lines(code_lines)
    print(blocks)

    field = np.zeros((N, N), dtype=np.int_)


if __name__ == '__main__':
    main()
