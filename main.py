from libs.run_bytecode import run_bytecode
from libs.utils import check_errors_and_compile, print_code_lines
from libs.server import server

N = 21

PROGRAM = '''

SET UP= 5
SET RIGHT=20
SET DOWN =   5
SET LEFT =5

PROCEDURE NEW2
  LEFT 1
ENDPROC

PROCEDURE NEW
  CALL CIRCLE
  LEFT 1
ENDPROC

PROCEDURE CIRCLE
  LEFT 1
  CALL NEW
ENDPROC

RIGHT RIGHT
CALL CIRCLE
CALL CIRCLE
CALL CIRCLE
CALL CIRCLE
CALL CIRCLE



'''

PROGRAM = '''

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

PROGRAM = '''
SET X = Z
SET Y = X
SET Z = Y

IFBLOCK LEFT

ENDIF

UP Z
PROCEDURE CIRCLE
  UP 9
  REPEAT 2
    UP 1
    RIGHT 1
  ENDREPEAT

  REPEAT 12
    RIGHT 1
  ENDREPEAT

  REPEAT 4
    RIGHT 1
    DOWN 1
  ENDREPEAT

  REPEAT 10
    DOWN 1
  ENDREPEAT

  LEFT 20
ENDPROC

REPEAT 9
  CALL CIRCLE
ENDREPEAT
'''


def main():
    server()
    N = 21

    error, source, bytecode_to_source, bytecode_lines = check_errors_and_compile(PROGRAM)
    print_code_lines(bytecode_lines, bytecode_to_source=bytecode_to_source)
    if error:
        return print(error)

    if error := run_bytecode(bytecode_lines, N):
        return print(f'Runtime error: {error}')


if __name__ == '__main__':
    main()
