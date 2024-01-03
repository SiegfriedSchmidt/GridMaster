import React, {useEffect, useRef, useState} from 'react';
import classes from "./Main.module.css";
import Executor from "../Executor/Executor";
import {compileCode} from "../../api/compileCode";
import {inflate} from "zlib";

const Main = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const executorRef = useRef<Executor>()
    const [code, setCode] = useState<string>('')

    useEffect(() => {
        const canvas = canvasRef.current as HTMLCanvasElement
        const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        const executor = new Executor(ctx, 40)
        executor.drawGrid()
        executorRef.current = executor
    }, [canvasRef])

    async function onClick() {
        const {success, message} = await compileCode(code)
        if (!success) {
            return alert(message)
        }
        const error = await executorRef.current?.run_bytecode(message)
        if (error) {
            alert(`Runtime error: ${error}`)
        }
    }

    return (
        <div className={classes.container}>
            <div className={classes.textExecContainer}>
                <textarea className={classes.code} rows={20} cols={50}
                          onChange={e => setCode(e.target.value)}></textarea>
                <canvas className={classes.field} ref={canvasRef}></canvas>
            </div>
            <button className={classes.button} onClick={onClick}>Submit</button>
        </div>
    );
};

export default Main;