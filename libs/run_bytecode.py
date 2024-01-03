from typing import List
import numpy as np
from libs.all_commands import BC
from libs.command_line_graph import Array, move_executor, show_field


def check_borders(x, y, register, N) -> str:
    if x >= N or x < 0 or y >= N or y < 0:
        return 'Border'

    register['RIGHT'] = int(x == N - 1)
    register['LEFT'] = int(x == 0)
    register['UP'] = int(y == N - 1)
    register['DOWN'] = int(y == 0)
    return ''


def run_bytecode(bytecode_lines: List[List], N):
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
                if border := check_borders(x, y, register, N):
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
