export default class Draw {
    private ctx: CanvasRenderingContext2D
    public lineWidth: number

    constructor(ctx: CanvasRenderingContext2D) {
        this.ctx = ctx
        this.lineWidth = 1
    }

    fillScreen(c: string) {
        this.Color(c)
        this.ctx.fillRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height)
    }

    Text(t: string, x: number, y: number, c: string, f: string) {
        this.Color(c)
        this.ctx.font = f
        this.ctx.fillText(t, x, y)
    }

    Color(c: string) {
        this.ctx.fillStyle = c
    }

    Rect(x: number, y: number, s: number, c: string) {
        this.Color(c)
        this.ctx.fillRect(x, y, s, s)
    }

    Circle(x: number, y: number, r: number, c: string) {
        this.Color(c)
        this.ctx.beginPath();
        this.ctx.arc(x, y, r, 0, 2 * Math.PI);
        this.ctx.fill();
    }

    Line(x1: number, y1: number, x2: number, y2: number, c: string) {
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.lineWidth = this.lineWidth;
        this.ctx.strokeStyle = c;
        this.ctx.stroke();
    }
}