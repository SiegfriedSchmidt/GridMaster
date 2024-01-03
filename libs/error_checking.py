from typing import List, Tuple
from libs.all_commands import C
import string

alphabet = list(string.ascii_letters)


def check_var(var: str, string_required=False) -> bool:
    if not string_required and var.isdigit():
        return 1 <= int(var) <= 1000
    else:
        return var[0] in alphabet


def check_command_syntax(code_lines: List[List[str]]) -> Tuple[str, int]:
    for idx, line in enumerate(code_lines):
        match line[0]:
            case C.RIGHT | C.LEFT | C.UP | C.DOWN | C.REPEAT:
                if len(line) == 2 and check_var(line[1]):
                    continue
            case C.PROCEDURE | C.CALL:
                if len(line) == 2 and check_var(line[1], True):
                    continue
            case C.IFBLOCK:
                if len(line) == 2 and line[1] in [C.RIGHT, C.LEFT, C.UP, C.DOWN]:
                    continue
            case C.SET:
                if len(line) < 4:
                    sep = "".join(line[1:]).split('=')
                    if len(sep) == 2:
                        line = [C.SET, sep[0], '=', sep[1]]

                if len(line) == 4 and not line[1][0].isdigit() and line[2] == '=' and check_var(line[3]):
                    line.pop(2)
                    code_lines[idx] = line
                    continue
            case C.ENDIF | C.ENDREPEAT | C.ENDPROC:
                if len(line) == 1:
                    continue
            case _:
                ...

        return 'Syntax error', idx
    return '', -1


def check_procedure_calls(code_lines: List[List[str]], jumping: List[int]) -> Tuple[str, int]:
    procedures = {}

    start = -1
    for idx, line in enumerate(code_lines):
        if line[0] == C.PROCEDURE:
            if start != -1:
                return 'Recursive declaration procedure', idx
            if line[1] in procedures:
                return 'Redeclaration procedure', idx
            start = idx
        elif line[0] == C.CALL:
            if start != -1 and code_lines[start][1] == line[1]:
                return 'Max nesting level exceeded', idx
            if (val := procedures.get(line[1], -1)) != -1:
                jumping[idx] = val
            else:
                return 'Call undefined procedure', idx
        elif line[0] == C.ENDPROC:
            procedures[code_lines[start][1]] = start
            start = -1

    return '', -1


def check_code_blocks(code_lines: List[List[str]], jumping: List[int]) -> Tuple[str, int]:
    alias = {
        C.IFBLOCK: 1,
        C.ENDIF: -1,
        C.REPEAT: 2,
        C.ENDREPEAT: -2,
        C.PROCEDURE: 3,
        C.ENDPROC: -3
    }

    stack = []
    for idx, line in enumerate(code_lines):
        if val := alias.get(line[0]):
            if val > 0:
                stack.append((val, idx))
            else:
                if len(stack) > 0 and (start := stack.pop())[0] == -val:
                    jumping[start[1]] = int(idx)
                    jumping[idx] = int(start[1])
                else:
                    return ' '.join(line), idx

    if len(stack) != 0:
        return "Construction not closed", stack[0][1]

    return '', -1


def check_max_nesting_limit(code_lines: List[List[str]], jumping: List[int]) -> Tuple[str, int]:
    nesting_vals = {
        C.IFBLOCK: 1,
        C.ENDIF: -1,
        C.REPEAT: 1,
        C.ENDREPEAT: -1,
        C.CALL: 1,
        C.PROCEDURE: 1,
        C.ENDPROC: -1
    }
    nesting = 0
    max_nesting = -1
    idx = 0
    stack = []
    while idx < len(code_lines):
        cmd = code_lines[idx][0]
        nesting += nesting_vals.get(cmd, 0)
        match cmd:
            case C.CALL:
                stack.append(idx)
                idx = jumping[idx]
            case C.ENDPROC:
                if len(stack) > 0:
                    idx = stack.pop()

        max_nesting = max(max_nesting, nesting)
        if max_nesting > 3:
            return 'Max nesting level exceeded', idx

        idx += 1

    return '', -1


def check_errors(code_lines: List[List[str]]) -> Tuple[Tuple[str, int], List[int]]:
    jumping = [-1 for i in range(len(code_lines))]

    if (error := check_command_syntax(code_lines))[0]:
        return error, jumping

    if (error := check_procedure_calls(code_lines, jumping))[0]:
        return error, jumping

    if (error := check_code_blocks(code_lines, jumping))[0]:
        return error, jumping

    if (error := check_max_nesting_limit(code_lines, jumping))[0]:
        return error, jumping

    return error, jumping


def check_all_errors(source, code_to_source: List[int], code_lines: List[List[str]]) -> Tuple[str, List[int]]:
    error, jumping = check_errors(code_lines)

    if (error := check_command_syntax(code_lines))[0]:
        source_idx = code_to_source[error[1]]
        return f'{error[0]} in line {source_idx + 1}: "{source[source_idx]}"', jumping

    return '', jumping
