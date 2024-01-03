import React, {useEffect, useRef, useState} from 'react';
import classes from "./Main.module.css";
import Executor from "../Executor/Executor";
import {compileCode} from "../../api/compileCode";
import CodeMirror from '@uiw/react-codemirror';

function setStartStyles(buttonRef: React.RefObject<HTMLButtonElement>) {
    if (buttonRef.current) {
        buttonRef.current.style.backgroundColor = 'greenyellow'
        buttonRef.current.innerText = 'Run'
    }
}

function setStopStyles(buttonRef: React.RefObject<HTMLButtonElement>) {
    if (buttonRef.current) {
        buttonRef.current.style.backgroundColor = 'orangered'
        buttonRef.current.innerText = 'Stop'
    }
}

const Main = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const executorRef = useRef<Executor>()
    const buttonRef = useRef<HTMLButtonElement>(null)
    const [code, setCode] = useState<string>('')

    useEffect(() => {
        const canvas = canvasRef.current as HTMLCanvasElement
        const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        const executor = new Executor(ctx, 40)
        executor.init()
        executorRef.current = executor
    }, [canvasRef])

    async function onClick(event: React.MouseEvent<HTMLButtonElement>) {
        if (executorRef.current?.running) {
            executorRef.current?.stop()
            setStartStyles(buttonRef)
        } else {
            const {success, message} = await compileCode(code)
            if (!success) {
                return alert(message)
            }
            setStopStyles(buttonRef)

            const error = await executorRef.current?.run(message, false)
            if (error) {
                setStartStyles(buttonRef)
                alert(`Runtime error: ${error}`)
            }
        }
    }

    return (
        <div className={classes.container}>
            <div className={classes.textExecContainer}>
                <CodeMirror
                    onChange={value => setCode(value)}
                    className={classes.code}
                    placeholder='Пишите, что хотите'
                    value=""
                    height="40vh"
                    theme="light"
                />
                {/*<textarea className={classes.code} rows={20} cols={50}*/}
                {/*          onChange={e => setCode(e.target.value)}></textarea>*/}
                <canvas className={classes.field} ref={canvasRef}></canvas>
            </div>
            <button style={{}} className={classes.button} ref={buttonRef} onClick={onClick}>Run</button>
        </div>
    );
};

export default Main;