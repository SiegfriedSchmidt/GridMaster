import React, {ChangeEvent, useEffect, useRef, useState} from 'react';
import classes from "./Main.module.css";
import Executor from "../Executor/Executor";
import {compileCode} from "../../api/compileCode";
import CodeMirror, {ReactCodeMirrorRef} from '@uiw/react-codemirror';
import Slider from "../Slider/Slider";
import Selector from "../Selector/Selector";
import {loadCodeDB} from "../../api/loadCodeDB";
import {saveCodeDB} from "../../api/saveCodeDB";

function setStartStyles(buttonRef: React.RefObject<any>, text: string) {
    if (buttonRef.current) {
        buttonRef.current.classList.remove(classes.buttonStop)
        buttonRef.current.innerText = text
    }
}

function setStopStyles(buttonRef: React.RefObject<any>, text: string) {
    if (buttonRef.current) {
        buttonRef.current.classList.add(classes.buttonStop)
        buttonRef.current.innerText = text
    }
}

const Main = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const executorRef = useRef<Executor>()
    const buttonRunRef = useRef<HTMLButtonElement>(null)
    const buttonLoadDBRef = useRef<HTMLDivElement>(null)
    const codeMirrorRef = useRef<ReactCodeMirrorRef>(null)
    const [delay, setDelay] = useState<number>(100)
    const [code, setCode] = useState<string>('')
    const [selected, setSelected] = useState<string>('')
    const [selecting, setSelecting] = useState<boolean>(false)

    async function loadCodeFromDB(index: string) {
        const res = await loadCodeDB(index)
        if (res.success) {
            setCode(res.message)
        } else {
            alert('Error loading from db')
        }
    }

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

    useEffect(() => {
        if (selecting) {
            setStartStyles(buttonLoadDBRef, 'Load db')
            setSelecting(!selecting)
            loadCodeFromDB(selected)
            setSelected('')
        }
    }, [selected])

    async function onClick(event: React.MouseEvent<HTMLButtonElement>) {
        if (executorRef.current?.running) {
            executorRef.current?.stop()
            setStartStyles(buttonRunRef, 'Run')
        } else {
            const {success, message} = await compileCode(code)
            if (!success) {
                return alert(message)
            }
            setStopStyles(buttonRunRef, 'Stop')

            const error = await executorRef.current?.run(message, true)
            if (error) {
                setTimeout(() => alert(error), 100)
            }
            setStartStyles(buttonRunRef, 'Run')
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

    async function loadCode() {
        if (selecting) {
            setStartStyles(buttonLoadDBRef, 'Load db')
        } else {
            setStopStyles(buttonLoadDBRef, 'Choose')
        }
        setSelecting(!selecting)
    }

    async function saveCode() {
        const res = await saveCodeDB(code)
        if (res.success) {
            alert(`Code successfully saved with index ${res.message}`)
        } else {
            alert('Error saving code into db')
        }
    }


    return (
        <div className={classes.container}>
            <div className={classes.settings}>
                <input id='import' type="file" onChange={importFile} style={{display: "none"}}/>
                <label className={classes.file} htmlFor="import">Import file</label>
                <div className={classes.file} onClick={exportFile}>Export file</div>
                <div className={classes.file} onClick={saveCode}>Save db</div>
                <div ref={buttonLoadDBRef} className={classes.file} onClick={loadCode}>Load db</div>
                <Selector setSelected={setSelected} selecting={selecting}/>
                <Slider setValue={setDelay}/>
                <input className={classes.checkbox} type="checkbox"
                       onChange={e => executorRef.current?.drawing_mode(e.target.checked)}/>
            </div>

            <div className={classes.textExecContainer}>
                <CodeMirror
                    ref={codeMirrorRef}
                    onChange={value => setCode(value)}
                    className={classes.code}
                    placeholder='Пишите код'
                    value={code}
                    height="40vh"
                    theme="light"
                />
                <canvas className={classes.field} ref={canvasRef}></canvas>
            </div>
            <div className={classes.buttonsContainer}>
                <button style={{}} className={classes.button} ref={buttonRunRef} onClick={onClick}>Run</button>
            </div>
        </div>
    );
};

export default Main;