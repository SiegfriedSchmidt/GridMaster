from typing import List, Dict, Tuple
from libs.all_commands import C, BC


def compile_into_bytecode(code_lines: List[List[str]], jumping: List[int]) -> Tuple[List[List], Dict[int, int]]:
    bytecode_lines: List[List] = []

    var_id = [0]
    label = {}
    register = {}
    register_line = {}

    def A(x: List):
        bytecode_lines.append(x)

    def new_reg():
        r = f'R{var_id[0]}'
        var_id[0] += 1
        return r

    def add_reg(var: str):
        if not (var in register):
            register[var] = new_reg()

    def S(var: str | int):
        if isinstance(var, int) or var.isdigit():
            A([BC.STORE_CONST, int(var)])
        else:
            add_reg(var)
            A([BC.STORE, register[var]])

    def J(var: int, displace=0):
        A([BC.JMP, var, displace])

    directions = {'RIGHT': (1, 0), "LEFT": (-1, 0), "UP": (0, 1), "DOWN": (0, -1)}
    for idx, line in enumerate(code_lines):
        label[idx] = len(bytecode_lines)
        match line[0]:
            case C.RIGHT | C.LEFT | C.UP | C.DOWN:
                S(line[1])
                A([BC.DISPLACE, *directions[line[0]]])
            case C.IFBLOCK:
                A([BC.STORE, line[1]])
                S(0)
                A([BC.CMP])
                J(jumping[idx])
            case C.REPEAT:
                S(line[1])
                register_line[idx] = (reg := new_reg())
                A([BC.MOV, reg])
                A([BC.STORE, reg])
                S(0)
                A([BC.CMP])
                J(jumping[idx], 2)
            case C.ENDREPEAT:
                A([BC.SUB, register_line[jumping[idx]]])
                J(jumping[idx], 2)
            case C.SET:
                S(line[2])
                add_reg(line[1])
                A([BC.MOV, register[line[1]]])
            case C.CALL:
                S(len(bytecode_lines) + 2)
                J(jumping[idx], 1)
            case C.PROCEDURE:
                J(jumping[idx], 1)
            case C.ENDPROC:
                A([BC.JMP])
            case _:
                ...

    for idx, line in enumerate(bytecode_lines):
        if line[0] == BC.JMP and len(line) > 1:
            bytecode_lines[idx] = [BC.JMP, label[line[1]] + int(line[2])]

    return bytecode_lines, label
