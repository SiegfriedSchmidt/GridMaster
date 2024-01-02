import numpy as np
from typing import List, Dict, Tuple
from pprint import pprint
from time import sleep
import colorama as cl

cl.init()

N = 21

PROGRAM = '''

SET UP= 50
SET RIGHT=50
SET DOWN =   50
SET LEFT =50

PROCEDURE TO_UP
ENDPROC

PROCEDURE TO_RIGHT
  CALL TO_UP
ENDPROC

PROCEDURE TO_DOWN
  IFBLOCK DOWN
    UP 19
  ENDIF
ENDPROC

PROCEDURE TO_LEFT
  CALL TO_RIGHT
  IFBLOCK LEFT
    RIGHT 19
  ENDIF
ENDPROC

  REPEAT UP
    CALL TO_UP
    UP 1
  ENDREPEAT
  
  REPEAT RIGHT
    CALL TO_RIGHT
    RIGHT 1
  ENDREPEAT

  REPEAT DOWN
    CALL TO_DOWN
    DOWN 1
  ENDREPEAT

  REPEAT LEFT
    CALL TO_LEFT
    LEFT 1
  ENDREPEAT
'''

PROGRAM2 = '''

UP 10
PROCEDURE CIRCLE
REPEAT 4
UP 1
RIGHT 1
ENDREPEAT

REPEAT 4
RIGHT 1
ENDREPEAT

REPEAT 4
RIGHT 1
DOWN 1
ENDREPEAT

REPEAT 4
DOWN 1
ENDREPEAT

LEFT 12
ENDPROC

REPEAT 10
CALL CIRCLE
ENDREPEAT
'''

PROGRAM2 = '''
SET X = 4
REPEAT X
RIGHT X
ENDREPEAT
SET X = 5
'''


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


class BC:
    DISPLACE = "DISPLACE"
    JMP = "JMP"
    CMP = "CMP"
    SUB = "SUB"
    MOV = "MOV"
    STORE = "STORE"
    STORE_CONST = "STORE_CONST"


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


def check_var(var: str, string_required=False) -> bool:
    if not string_required and var.isdigit():
        return 1 <= int(var) <= 1000
    else:
        return not var[0].isdigit()


def check_command_syntax(code_lines: List[List[str]]) -> str:
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

        return ' '.join(line)
    return ''


def check_procedure_calls(code_lines: List[List[str]], jumping: List[int]) -> str:
    procedures = {}

    start = -1
    for idx, line in enumerate(code_lines):
        if line[0] == C.PROCEDURE:
            if start != -1:
                return f'Recursive declaration procedure "{" ".join(line)}"'
            if line[1] in procedures:
                return f'Redeclaration procedure "{" ".join(line)}"'
            start = idx
        elif line[0] == C.CALL:
            if start != -1 and code_lines[start][1] == line[1]:
                return f'Recursive call procedure "{" ".join(line)}"'
            if (val := procedures.get(line[1], -1)) != -1:
                jumping[idx] = val
            else:
                return f'Call undefined procedure "{" ".join(line)}"'
        elif line[0] == C.ENDPROC:
            procedures[code_lines[start][1]] = start
            start = -1

    return ''


def check_code_blocks(code_lines: List[List[str]], jumping: List[int]) -> str:
    alias = {
        C.IFBLOCK: 1,
        C.ENDIF: -1,
        C.REPEAT: 2,
        C.ENDREPEAT: -2,
        C.PROCEDURE: 3,
        C.ENDPROC: -3
    }
    alias_ = {y: x for x, y in alias.items()}

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
                    return ' '.join(line)

    if len(stack) != 0:
        return f"Construction not closed {alias_[stack[0]]}"

    return ''


def check_max_nesting_limit(code_lines: List[List[str]], jumping: List[int]) -> str:
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
        idx += 1

    if max_nesting > 3:
        return f'Max nesting level exceeded'

    return ''


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


class Array(np.ndarray):
    def __setitem__(self, key, value):
        super().__setitem__((key[0], N - key[1] - 1), value)


def show_field(field):
    for y in range(N):
        for x in range(N):
            if field[x, y]:
                print(f'{cl.Fore.GREEN}X{cl.Fore.RESET}', end='  ')
            else:
                print('0', end='  ')
        print()
    print()


def move_executor(field, x, y, vx, vy, n):
    for i in range(n):
        field[x, y] = 0
        x += vx
        y += vy
        field[x, y] = 1
        print(f'\x1b[{N + 1}A\r\033[K', end='')
        show_field(field)

        sleep(0.1)


def check_borders(x, y, register) -> str:
    if x >= N or x < 0 or y >= N or y < 0:
        return 'Border'

    register['RIGHT'] = int(x == N - 1)
    register['LEFT'] = int(x == 0)
    register['UP'] = int(y == N - 1)
    register['DOWN'] = int(y == 0)
    return ''


def run_bytecode(bytecode_lines: List[List]):
    field = Array((N, N), dtype=np.bool_)
    field.fill(0)
    x, y = 0, 0
    field[x, y] = 1
    print()
    show_field(field)

    register = {'LEFT': 1, 'UP': 0, 'RIGHT': 0, 'DOWN': 1}
    stack = []
    idx = 0
    while idx < len(bytecode_lines):
        line = bytecode_lines[idx]
        cmd = line[0]
        args = line[1:] if len(line) > 1 else None

        if cmd in [BC.SUB, BC.STORE]:
            if not (args[0] in register):
                return 'Using undefined variable'

        match cmd:
            case BC.DISPLACE:
                n = stack.pop()
                x += n * args[0]
                y += n * args[1]
                if border := check_borders(x, y, register):
                    return border
                move_executor(field, x - n * args[0], y - n * args[1], args[0], args[1], n)
            case BC.JMP:
                idx = (args[0] if args else stack.pop()) - 1
            case BC.CMP:
                if stack.pop() != stack.pop():
                    idx += 1
            case BC.SUB:
                register[args[0]] -= 1
            case BC.MOV:
                register[args[0]] = stack.pop()
            case BC.STORE:
                stack.append(register[args[0]])
            case BC.STORE_CONST:
                stack.append(args[0])

        idx += 1
        # print(idx, cmd, args, register, stack)


def main():
    code_lines = initial_preparations(PROGRAM)
    jumping = [-1 for i in range(len(code_lines))]
    print_code_lines(code_lines)

    if error := check_command_syntax(code_lines):
        return print(f'Syntax error: {error}')

    if error := check_procedure_calls(code_lines, jumping):
        return print(f'Procedure declaration error: {error}')

    if error := check_code_blocks(code_lines, jumping):
        return print(f'Nesting error: {error}')

    if error := check_max_nesting_limit(code_lines, jumping):
        return print(f'Nesting error: {error}')

    bytecode_lines, label = compile_into_bytecode(code_lines, jumping)

    print()
    print_code_lines(bytecode_lines, label=label)

    if error := run_bytecode(bytecode_lines):
        return print(f'Runtime error: {error}')


if __name__ == '__main__':
    main()

'''
REPEAT X
ENDREPEAT

0 1 MOV R3, 0
0 2 LOAD R3
0 3 LOAD R4
1 4 CMP
0 5 JUMP 8
0 6 SUB R3
0 7 JUMP 2
-1 8 





7 ADD R3, 1
8 JUMP 3
9 

IFBLOCK LEFT
LEFT X
ENDIF

1 LOAD R-4
2 LOAD_CONST 0
3 CMP
4 JUMP 8
5 LOAD_CONST 10
6 LOAD_CONST 0
7 DISPLACE 
8 

if left:    
    x -= 10
elif right:
    x += 10
elif up:
    y += 10
    
p += v

SET X = 5

1 LOAD_CONST 5
2 MOV R1



PROCEDURE func
SET X = 5
ENDPROC

CALL func
LEFT X


PROCEDURE func2
REPEAT 5
ENDREPEAT
ENDPROC

PROCEDURE func1
CALL func2
ENDPROC

REPEAT 1
CALL func1
ENDREPEAT

'''
