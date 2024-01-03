import Draw from "../Draw/Draw";

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

    check_border(x: number, y: number, register: { [key: string]: number }): string {
        if (x >= this.N || x < 0 || y >= this.N || y < 0) {
            return "Border"
        }
        register['RIGHT'] = Number(x === this.N - 1)
        register['LEFT'] = Number(x === 0)
        register['UP'] = Number(y === this.N - 1)
        register['DOWN'] = Number(y === 0)
        return ''
    }

    draw_executor(x: number, y: number, c: string) {
        this.draw.Rect(x * this.sz + this.p + 2, (this.N - y - 1) * this.sz + this.p + 2, this.sz - 4, c)
    }

    async move_executor(x: number, y: number, vx: number, vy: number, n: number) {
        for (let i = 0; i < n; i++) {
            this.draw_executor(x, y, 'white')
            x += vx
            y += vy
            this.draw_executor(x, y, 'black')
            await sleep(100)
        }
    }

    async run_bytecode(bytecode: string[][]): Promise<string> {
        this.drawGrid()
        let x = 0
        let y = 0
        this.draw_executor(x, y, 'black')
        const register: { [key: string]: number } = {'LEFT': 1, 'UP': 0, 'RIGHT': 0, 'DOWN': 1}
        const stack: number[] = []
        let idx = 0

        while (idx < bytecode.length) {
            const cmd = bytecode[idx][0]
            const args = bytecode[idx].length > 1 ? bytecode[idx].slice(1).map(e => Number(e)) : []

            if ([BC.SUB, BC.STORE, BC.MOV].includes(cmd as BC)) {
                console.log(args[0], register)
                if (!(args[0] in register)) {
                    return 'Using undefined variable'
                }
            }

            switch (cmd) {
                case BC.DISPLACE:
                    const n = stack.pop() as number
                    x += n * args[0]
                    y += n * args[1]
                    const border = this.check_border(x, y, register)
                    if (border) {
                        return border
                    }
                    await this.move_executor(x - n * args[0], y - n * args[1], args[0], args[1], n)
                    break
                case BC.JMP:
                    idx = (args.length > 0 ? args[0] : stack.pop() as number) - 1
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
                    stack.push(args[0])
                    break
            }

            ++idx
        }

        return ''
    }
}