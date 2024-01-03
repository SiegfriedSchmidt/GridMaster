import numpy as np
import colorama as cl
from time import sleep

cl.init()


class Array(np.ndarray):
    def __setitem__(self, key, value):
        super().__setitem__((key[0], self.shape[1] - key[1] - 1), value)


def show_field(field: np.ndarray):
    for y in range(field.shape[1]):
        for x in range(field.shape[0]):
            if field[x, y]:
                print(f'{cl.Fore.GREEN}X{cl.Fore.RESET}', end='  ')
            else:
                print('0', end='  ')
        print()
    print()


def move_executor(field: np.ndarray, x, y, vx, vy, n):
    for i in range(n):
        field[x, y] = 0
        x += vx
        y += vy
        field[x, y] = 1
        print(f'\x1b[{field.shape[0] + 1}A\r\033[K', end='')
        show_field(field)

        sleep(0.1)
