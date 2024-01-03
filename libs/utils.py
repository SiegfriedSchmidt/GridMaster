from typing import List, Tuple
from libs.compile_bytecode import compile_into_bytecode
from libs.error_checking import check_all_errors


def print_code_lines(code_lines: List[List[str]], changes=None, label=None):
    if label:
        label = {y: x for x, y in label.items()}
    for idx, line in enumerate(code_lines):
        if changes:
            print(f'{idx:<2} {changes[idx]:<2} {" ".join([str(l) for l in line])} ')
        elif label:
            print(f'{idx:<2} {label.get(idx, "-"):<2} {" ".join([str(l) for l in line])} ')
        else:
            print(f'{idx:<2} {" ".join([str(l) for l in line])}')


def initial_preparations(code: str) -> List[List[str]]:
    return list(filter(lambda l: len(l) > 0, map(lambda s: s.strip().split(), code.strip().splitlines())))


def check_errors_and_compile(code: str) -> Tuple[str, List[List[str]], List[List[str]]]:
    code_lines = initial_preparations(code)
    error, jumping = check_all_errors(code_lines)
    if error:
        return error, code_lines, code_lines

    bytecode_lines, label = compile_into_bytecode(code_lines, jumping)
    return error, code_lines, bytecode_lines
