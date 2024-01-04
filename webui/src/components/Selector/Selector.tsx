import React, {Dispatch, FC, SetStateAction, useEffect, useRef, useState} from 'react';
import classes from "./Selector.module.css";
import {getAllCodes} from "../../api/getAllCodes";

interface SelectorInterface {
    setSelected: Dispatch<SetStateAction<string>>
    selecting: boolean
}

const Selector: FC<SelectorInterface> = ({setSelected, selecting}) => {
    const selectRef = useRef<HTMLSelectElement>(null)
    const [list, setList] = useState<string[]>([])

    async function loadList() {
        const res = await getAllCodes()
        if (res.success) {
            setList(res.message)
        } else {
            alert('Error')
        }
    }

    useEffect(() => {
        if (selectRef.current) {
            selectRef.current.disabled = !selecting
            if (!selectRef.current.disabled) {
                loadList()
            }
        }
    }, [selecting])


    function onSelect(e: React.SyntheticEvent<HTMLSelectElement, Event>) {
        if (selectRef.current) {
            if (selectRef.current.selectedIndex !== -1) {
                setSelected(e.currentTarget.options[e.currentTarget.selectedIndex].value)
                selectRef.current.selectedIndex = -1
            }
        }
    }

    return (
        <select className={classes.selector} onChange={onSelect} size={3} ref={selectRef}>
            {list.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
    )
}

export default Selector