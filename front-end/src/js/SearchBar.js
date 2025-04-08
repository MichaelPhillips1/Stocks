import { React, useState} from 'react';
import ArrowDropDownCircleIcon from '@mui/icons-material/ArrowDropDownCircle';
import { Checkbox } from '@mui/material';
import axios from 'axios';

function SearchBar(){

    const [indicatorDropDownOpen, setIndicatorDropDownOpen] = useState(false);
    const [ticker, setTicker] = useState("")

    function calcPosition(min, max, value, height){
        let offset = (value - min) / (max - min)
        return ((.95 * height) * offset) + (.025 * height)
    }

    function fillPriceChart(data){
        let canvas = document.getElementById("PriceChart");
        if(!canvas) return;
        let canvasDrawer = canvas.getContext('2d');

        let max = Math.max(...data)
        let min = Math.min(...data)

        canvasDrawer.moveTo(0, canvas.height - calcPosition(min, max, data[0], canvas.height))
        for(let i = 1; i < data.length; i++){
            canvasDrawer.lineTo(canvas.width * (i / (data.length - 1)), canvas.height - calcPosition(min, max, data[i], canvas.height))
        }

        canvasDrawer.strokeStyle = "green"
        canvasDrawer.stroke();

        canvasDrawer.lineTo(canvas.width, canvas.height)
        canvasDrawer.lineTo(0, canvas.height)
        canvasDrawer.closePath()

        canvasDrawer.fillStyle = "rgba(0, 255, 0, .05)"
        canvasDrawer.fill()
    }

    async function initializeSearch(){
        axios.get('http://127.0.0.1:5000/PriceData',{params:{ticker: ticker}}).then(response => {fillPriceChart(response.data.PriceData)})
        axios.get('http://127.0.0.1:5000/MACDData',{params:{ticker: ticker}}).then(response => {console.log(response)})
        axios.get('http://127.0.0.1:5000/RSIData',{params:{ticker: ticker}}).then(response => {console.log(response)})
    }

    return <div id="SearchBodyContainer">
            <div id="SearchHeadContainer"><input id="SearchBarInput" onChange={(e) => setTicker(e.target.value)}></input><button id="SearchBarButton" onClick={() => initializeSearch()}>Search</button></div>
            <button id="SearchBarIndicatorDropdownButton" onClick={() => {setIndicatorDropDownOpen(!indicatorDropDownOpen)}}>
                Technicals <ArrowDropDownCircleIcon/>
            </button>
            <div id="SearchIndicatorSelecitonDiv" style={!indicatorDropDownOpen ? {opacity: "0", padding: '0px', margin:'0px', transform: 'scaley(0)', maxHeight: '0px', height: "0%"} : {}}>
                <div id="SearchIndicatorSelectionWrapper" style={!indicatorDropDownOpen ? {visibility: 'hidden', width: '100%'} : {width: '100%'}}>
                    <div><Checkbox></Checkbox> RSI</div>
                    <div><Checkbox></Checkbox> MACD</div>
                </div>
            </div>
            <p>Prices</p>
            <canvas id="PriceChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            <p>MACD</p>
            <canvas id="MACDChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
            <p>RSI</p>
            <canvas id="RSIChart" width={(window.innerWidth * .75)} height={(window.innerHeight * .75)}></canvas>
        </div>
}


export default SearchBar;