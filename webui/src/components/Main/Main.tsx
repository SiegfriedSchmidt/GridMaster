import React, {ChangeEvent, MouseEventHandler, useEffect, useRef, useState} from 'react';
import classes from "./Main.module.css";
import Executor from "../Executor/Executor";
import {compileCode} from "../../api/compileCode";
import CodeMirror, {ReactCodeMirrorRef} from '@uiw/react-codemirror';
import Slider from "../Slider/Slider";

function setStartStyles(buttonRef: React.RefObject<HTMLButtonElement>) {
    if (buttonRef.current) {
        buttonRef.current.classList.remove(classes.buttonStop)
        buttonRef.current.innerText = 'Run'
    }
}

function setStopStyles(buttonRef: React.RefObject<HTMLButtonElement>) {
    if (buttonRef.current) {
        buttonRef.current.classList.add(classes.buttonStop)
        buttonRef.current.innerText = 'Stop'
    }
}

const Main = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const executorRef = useRef<Executor>()
    const buttonRef = useRef<HTMLButtonElement>(null)
    const codeMirrorRef = useRef<ReactCodeMirrorRef>(null)
    const [delay, setDelay] = useState<number>(100)
    const [code, setCode] = useState<string>('')

    useEffect(() => {
        const canvas = canvasRef.current as HTMLCanvasElement
        const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        const executor = new Executor(ctx, 40)
        executor.init()
        executorRef.current = executor
    }, [canvasRef])

    useEffect(() => {
        executorRef.current?.set_delay(delay)
    }, [delay])

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

            const error = await executorRef.current?.run(message, true)
            if (error) {
                setTimeout(() => alert(error), 100)
            }
            setStartStyles(buttonRef)
        }
    }


    async function importFile(e: ChangeEvent<HTMLInputElement>) {
        let file = e.target.files![0];
        let reader = new FileReader();
        reader.readAsText(file);
        e.target.value = ''
        reader.onload = () => {
            if (typeof reader.result === 'string') {
                setCode(reader.result)
            } else {
                alert(`Error file reading: ${reader.error}`)
            }
        }
        reader.onerror = () => {
            alert(`Error file reading: ${reader.error}`)
        }
    }

    function downloadFile(filename: string, text: string) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    async function exportFile() {
        downloadFile('Program.txt', code)
    }

    return (
        <div className={classes.container}>
            <div className={classes.settings}>
                <input className={classes.checkbox} type="checkbox"
                       onChange={e => executorRef.current?.drawing_mode(e.target.checked)}/>
                <Slider setValue={setDelay}/>
                <input id='import' type="file" onChange={importFile} style={{display: "none"}}/>
                <label className={classes.file} htmlFor="import">Import</label>
                <div className={classes.file} onClick={exportFile}>Export</div>
            </div>

            <div className={classes.textExecContainer}>
                <CodeMirror
                    ref={codeMirrorRef}
                    onChange={value => setCode(value)}
                    className={classes.code}
                    placeholder='Пишите, что хотите'
                    value={code}
                    height="40vh"
                    theme="light"
                />
                <canvas className={classes.field} ref={canvasRef}></canvas>
            </div>
            <div className={classes.buttonsContainer}>
                <button style={{}} className={classes.button} ref={buttonRef} onClick={onClick}>Run</button>
            </div>
        </div>
    );
};

export default Main;