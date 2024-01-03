import React, {Dispatch, FC, SetStateAction, useRef} from 'react';
import classes from "./Slider.module.css";

interface SliderInterface {
    setValue: Dispatch<SetStateAction<number>>
}

const Slider: FC<SliderInterface> = ({setValue}) => {

    const inputRef = useRef<HTMLInputElement>(null)

    return (
        <input className={classes.slider} ref={inputRef} onInput={e => setValue(Number(e.currentTarget.value))}
               type="range" min="1" max="200" defaultValue="100"/>
    )
}

export default Slider