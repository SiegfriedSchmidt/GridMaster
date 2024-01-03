from typing import List, Tuple
from libs.compile_bytecode import compile_into_bytecode
from libs.error_checking import check_all_errors


def reverse_dict(d):
    return {y: x for x, y in d.items()}


def print_code_lines(code_lines: List[List[str]], changes=None, bytecode_to_source=None):
    for idx, line in enumerate(code_lines):
        if changes:
            print(f'{idx:<2} {changes[idx]:<2} {" ".join([str(l) for l in line])} ')
        elif bytecode_to_source:
            print(f'{idx:<2} {bytecode_to_source[idx]:<2} {" ".join([str(l) for l in line])} ')
        else:
            print(f'{idx:<2} {" ".join([str(l) for l in line])}')


def initial_preparations(code: str) -> Tuple[List[str], List[int], List[List[str]]]:
    source = list(map(lambda s: s.strip(), code.splitlines()))
    code_to_source = []
    lines = []
    for idx, line in enumerate(map(lambda s: s.upper().split(), source)):
        if len(line) > 0:
            code_to_source.append(idx)
            lines.append(line)

    return source, code_to_source, lines


def compare_bytecode_to_source(bytecode_lines, label, code_to_source) -> List[int]:
    bytecode_to_source = []
    label = reverse_dict(label)
    code_idx = 0
    for idx in range(len(bytecode_lines)):
        code_idx = label.get(idx, code_idx)
        bytecode_to_source.append(code_to_source[code_idx])

    return bytecode_to_source


def check_errors_and_compile(code: str) -> tuple[str, None, None, None] | tuple[str, List[str], List[int], List[List]]:
    source, code_to_source, code_lines = initial_preparations(code)
    error, jumping = check_all_errors(source, code_to_source, code_lines)
    if error:
        return error, None, None, None

    bytecode_lines, label = compile_into_bytecode(code_lines, jumping)
    bytecode_to_source = compare_bytecode_to_source(bytecode_lines, label, code_to_source)

    return error, source, bytecode_to_source, bytecode_lines
