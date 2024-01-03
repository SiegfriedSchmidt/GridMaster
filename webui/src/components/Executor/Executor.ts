import Draw from "../Draw/Draw";
import compiledType from "../../types/compiledType";

// const initField = (sx: number, sy: number, value: any) => new Array(sx).fill(value).map(() => new Array(sy).fill(value));

async function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

enum BC {
    DISPLACE = "DISPLACE",
    JMP = "JMP",
    CMP = "CMP",
    SUB = "SUB",
    MOV = "MOV",
    STORE = "STORE",
    STORE_CONST = "STORE_CONST",
}

export default class Executor {
    public readonly N = 21
    public readonly size: number
    public readonly sz: number
    public readonly p: number
    public running = false
    public drawing = false
    public delay = 100
    private readonly draw: Draw

    constructor(
        public readonly ctx: CanvasRenderingContext2D,
        public readonly pad: number
    ) {
        this.size = Math.floor(Math.min(window.innerHeight / 2, window.innerWidth / 2))
        this.sz = Math.floor((this.size - this.pad) / this.N)
        this.p = (this.size - this.sz * this.N) / 2
        this.draw = new Draw(ctx)
        this.ctx.canvas.height = this.size
        this.ctx.canvas.width = this.size
    }

    init() {
        this.drawGrid()
        this.drawGrid()
    }

    drawGrid() {
        for (let x = 0; x <= this.N; ++x) {
            this.ctx.moveTo(this.p + x * this.sz, this.p);
            this.ctx.lineTo(this.p + x * this.sz, this.N * this.sz + this.p);
        }

        for (let y = 0; y <= this.N; ++y) {
            this.ctx.moveTo(this.p, this.p + y * this.sz);
            this.ctx.lineTo(this.N * this.sz + this.p, this.p + y * this.sz);
        }

        for (let i = 0; i < this.N; i++) {
            for (let j = 0; j < this.N; j++) {
                this.draw_executor(i, j, 'white')
            }
        }

        this.ctx.strokeStyle = "black";
        this.ctx.stroke();
        this.draw_executor(0, 0, 'black')
    }

    check_border(x: number, y: number): string {
        if (x >= this.N || x < 0 || y >= this.N || y < 0) {
            return "Border"
        }
        return ''
    }

    border_registers(x: number, y: number, register: { [key: string]: number }) {
        register['RIGHT'] = Number(x === this.N - 1)
        register['LEFT'] = Number(x === 0)
        register['UP'] = Number(y === this.N - 1)
        register['DOWN'] = Number(y === 0)
    }

    draw_executor(x: number, y: number, c: string) {
        this.draw.Rect(x * this.sz + this.p + 2, (this.N - y - 1) * this.sz + this.p + 2, this.sz - 4, c)
    }

    drawing_mode(mode: boolean) {
        this.drawing = mode
    }

    set_delay(delay: number) {
        this.delay = delay
    }

    async move_executor(x: number, y: number, vx: number, vy: number, n: number): Promise<string> {
        for (let i = 0; i < n; i++) {
            await sleep(this.delay)
            if (!this.running) {
                return 'Stopped'
            }

            if (this.check_border(x + vx, y + vy)) {
                return "Border"
            }

            if (!this.drawing) {
                this.draw_executor(x, y, 'white')
            }

            x += vx
            y += vy
            this.draw_executor(x, y, 'black')
        }
        return ''
    }

    async run(bytecode: compiledType, logs: boolean): Promise<string> {
        this.running = true
        const {error, line} = await this.run_bytecode(bytecode.bytecodeLines, logs)
        this.running = false
        if (error) {
            const sourceLine = bytecode.bytecodeToSource[line]
            return `Runtime error "${error}" in line ${sourceLine + 1}: "${bytecode.source[sourceLine]}"`
        }
        return ''
    }

    async stop() {
        this.running = false
    }

    async run_bytecode(bytecode: string[][], logs: boolean): Promise<{ error: string, line: number }> {
        if (logs) console.clear()
        this.drawGrid()
        let x = 0
        let y = 0
        this.draw_executor(x, y, 'black')
        const register: { [key: string]: number } = {'LEFT': 1, 'UP': 0, 'RIGHT': 0, 'DOWN': 1}
        const stack: number[] = []
        let idx = 0

        while (idx < bytecode.length) {
            const cmd = bytecode[idx][0]
            const args = bytecode[idx].length > 1 ? bytecode[idx].slice(1) : []

            console.info(cmd, args, stack)

            if ([BC.SUB, BC.STORE].includes(cmd as BC)) {
                if (!(args[0] in register)) {
                    return {error: 'Using undefined variable', line: idx}
                }
            }

            switch (cmd) {
                case BC.DISPLACE:
                    const n = stack.pop() as number
                    const result = await this.move_executor(x, y, Number(args[0]), Number(args[1]), n)
                    if (result === 'Border') {
                        return {error: 'Border', line: idx}
                    } else if (result === "Stopped") {
                        return {error: '', line: -1}
                    }
                    x += n * Number(args[0])
                    y += n * Number(args[1])
                    this.border_registers(x, y, register)
                    break
                case BC.JMP:
                    idx = (args.length > 0 ? Number(args[0]) : stack.pop() as number) - 1
                    break
                case BC.CMP:
                    if (stack.pop() !== stack.pop()) {
                        idx += 1
                    }
                    break
                case BC.SUB:
                    register[args[0]] -= 1
                    break
                case BC.MOV:
                    register[args[0]] = stack.pop() as number
                    break
                case BC.STORE:
                    stack.push(register[args[0]])
                    break
                case BC.STORE_CONST:
                    stack.push(Number(args[0]))
                    break
            }

            ++idx
        }

        return {error: '', line: -1}
    }
}