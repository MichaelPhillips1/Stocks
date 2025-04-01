import { React, useEffect, useState, useRef} from 'react';
import ArrowDropDownCircleIcon from '@mui/icons-material/ArrowDropDownCircle';
import { Checkbox, getTableHeadUtilityClass } from '@mui/material';
import { height, margin, maxHeight, width } from '@mui/system';

function SearchBar(){

    const [indicatorDropDownOpen, setIndicatorDropDownOpen] = useState(false);

    function calcPosition(min, max, value, height){
        let offset = (value - min) / (max - min)
        return (.025 * height) + ((.95 * height) * offset)
    }

    useEffect(() => {
        let canvas = document.getElementById("PriceChart");
        if(!canvas) return;
        let canvasDrawer = canvas.getContext('2d');

        //Temp Data
        let data = [100, 104, 102, 106, 115, 104, 130, 125, 126, 124, 126, 134, 132, 132, 131, 132, 129, 127]
        let max = Math.max(...data)
        let min = Math.min(...data)

        canvasDrawer.moveTo(0, canvas.height - calcPosition(min, max, data[0], canvas.height))
        for(let i = 1; i < data.length; i++){
            canvasDrawer.lineTo(canvas.width * (i / data.length), canvas.height - calcPosition(min, max, data[i], canvas.height))
        }
        canvasDrawer.stroke();
    }, [])

    return <div id="SearchBodyContainer">
            <input id="SearchBarInput"></input>
            <button id="SearchBarIndicatorDropdownButton" onClick={() => {setIndicatorDropDownOpen(!indicatorDropDownOpen)}}>
                Technicals <ArrowDropDownCircleIcon/>
            </button>
            <div id="SearchIndicatorSelecitonDiv" style={!indicatorDropDownOpen ? {opacity: "0", padding: '0px', margin:'0px', transform: 'scaley(0)', maxHeight: '0px', height: "0%"} : {}}>
                <div id="SearchIndicatorSelectionWrapper" style={!indicatorDropDownOpen ? {visibility: 'hidden', width: '100%'} : {width: '100%'}}>
                    <div><Checkbox></Checkbox> RSI</div>
                    <div><Checkbox></Checkbox> MACD</div>
                    <div><Checkbox></Checkbox> BOLLINGER</div>
                    <div><Checkbox></Checkbox> ICHIMOKU</div>
                    <div><Checkbox></Checkbox> GOLDEN CROSS</div>
                </div>
            </div>
            PRICES
            <canvas id="PriceChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            RSI
            <canvas id="RSIChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            MACD
            <canvas id="MACDChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            BOLLINGER
            <canvas id="BollingerChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            ICHIMOKU
            <canvas id="IchimokuChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            GOLDEN CROSS
            <canvas id="GoldenCrossChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
        </div>
}


export default SearchBar;