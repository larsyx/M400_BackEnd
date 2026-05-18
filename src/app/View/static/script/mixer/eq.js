const fs = 48000;
const svg = d3.select("#eqChart");
let width = svg.node().clientWidth;
let height = +svg.node().clientHeight;

const margin = { top: 20, right: 20, bottom: 30, left: 50 };
let plotWidth = width - margin.left - margin.right;
let plotHeight = height - margin.top - margin.bottom;

const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

let xScale = d3.scaleLog().domain([20, 20000]).range([0, plotWidth]);
let yScale = d3.scaleLinear().domain([-15, 15]).range([plotHeight, 0]);

let xAxis = d3.axisBottom(xScale).ticks(10, ",.0f");
let yAxis = d3.axisLeft(yScale);

let xGrid = d3.axisBottom(xScale).ticks(10).tickSize(-plotHeight).tickFormat('');
let yGrid = d3.axisLeft(yScale).ticks(10).tickSize(-plotWidth).tickFormat('');

const gridX = g.append("g").attr("class", "grid-x").attr("transform", `translate(0,${plotHeight})`).call(xGrid);
const gridY = g.append("g").attr("class", "grid-y").call(yGrid);

const axisX = g.append("g").attr("transform", `translate(0,${plotHeight})`).call(xAxis);
const axisY = g.append("g").call(yAxis);

g.append("text")
  .attr("class", "x-label")
  .attr("x", plotWidth / 2)
  .attr("y", plotHeight + 30)
  .attr("text-anchor", "middle")
  .text("Frequenza (Hz)");

g.append("text")
  .attr("class", "y-label")
  .attr("transform", "rotate(-90)")
  .attr("x", -plotHeight / 2)
  .attr("y", -40)
  .attr("text-anchor", "middle")
  .text("Gain (dB)");

let bands = [
  { id: 0, freq: 100, gain: 0, q: 0.8 },
  { id: 1, freq: 500, gain: 0, q: 1.0 },
  { id: 2, freq: 2000, gain: 0, q: 1.0 },
  { id: 3, freq: 8000, gain: 0, q: 0.8 }
];

function complexDiv(nRe, nIm, dRe, dIm) {
  const denom = dRe*dRe + dIm*dIm;
  return {
    re: (nRe * dRe + nIm * dIm) / denom,
    im: (nIm * dRe - nRe * dIm) / denom
  };
}

function calcCoeffs(freq, gainDb, q) {
  const A = Math.pow(10, gainDb / 40);
  const w0 = 2 * Math.PI * freq / fs;
  const alpha = Math.sin(w0) / (2 * q);
  const b0 = 1 + alpha * A;
  const b1 = -2 * Math.cos(w0);
  const b2 = 1 - alpha * A;
  const a0 = 1 + alpha / A;
  const a1 = -2 * Math.cos(w0);
  const a2 = 1 - alpha / A;
  return {b0,b1,b2,a0,a1,a2};
}

function generateFreqs() {
  let f = 20;
  const arr = [];
  while (f <= 20000) {
    arr.push(f);
    f *= 1.05;
  }
  return arr;
}

function generateCurve() {
  const points = [];
  const freqs = generateFreqs();
  for (const f of freqs) {
    const omega = 2 * Math.PI * f / fs;
    const cos_omega = Math.cos(omega);
    const sin_omega = Math.sin(omega);
    const cos_2omega = Math.cos(2 * omega);
    const sin_2omega = Math.sin(2 * omega);
    let H_total = {re:1, im:0};
    for (const band of bands) {
      const {b0,b1,b2,a0,a1,a2} = calcCoeffs(band.freq, band.gain, band.q);
      const numRe = b0 + b1 * cos_omega + b2 * cos_2omega;
      const numIm = -b1 * sin_omega - b2 * sin_2omega;
      const denRe = a0 + a1 * cos_omega + a2 * cos_2omega;
      const denIm = -a1 * sin_omega - a2 * sin_2omega;
      const H = complexDiv(numRe, numIm, denRe, denIm);
      const re = H_total.re * H.re - H_total.im * H.im;
      const im = H_total.re * H.im + H_total.im * H.re;
      H_total = {re, im};
    }
    const mag = Math.sqrt(H_total.re**2 + H_total.im**2);
    const gainDb = 20 * Math.log10(mag);
    points.push({ freq: f, gain: gainDb });
  }
  return points;
}

let line = d3.line()
  .x(d => xScale(d.freq))
  .y(d => yScale(d.gain))
  .curve(d3.curveMonotoneX);

let area = d3.area()
  .x(d => xScale(d.freq))
  .y0(yScale(0))
  .y1(d => yScale(d.gain))
  .curve(d3.curveMonotoneX);

let areaPath = g.append("path")
  .datum(generateCurve())
  .attr("fill", "rgba(30,144,255,0.3)")
  .attr("stroke", "none")
  .attr("d", area);

let curvePath = g.append("path")
  .datum(generateCurve())
  .attr("fill", "none")
  .attr("stroke", "blue")
  .attr("stroke-width", 2)
  .attr("d", line);

let points = g.selectAll(".control-point")
  .data(bands)
  .enter()
  .append("circle")
  .attr("class", "control-point")
  .attr("r", 10)
  .attr("cx", d => xScale(d.freq))
  .attr("cy", d => yScale(d.gain))
  .call(d3.drag()
    .on("drag", function (event, d) {
      d.freq = Math.min(20000, Math.max(20, xScale.invert(event.x)));
      d.gain = Math.min(15, Math.max(-15, yScale.invert(event.y)));
      if (d.id === 0 || d.id === 3) d.q = 0.8;
      update();

      setEQ(d.id, 'freq', d.freq.toFixed(2));
      setEQ(d.id, 'gain', d.gain.toFixed(2));
    })
  );

function updateScales() {
  width = svg.node().clientWidth;
  plotWidth = width - margin.left - margin.right;
  height = svg.node().clientHeight;
  plotHeight = height -margin.top - margin.bottom;
  xScale.range([0, plotWidth]);
  yScale.range([plotHeight, 0]);

  xGrid = d3.axisBottom(xScale)
  .ticks(10)
  .tickSize(-plotHeight)  // deve essere negativo sull'asse Y, quindi corretto così
  .tickFormat('');

  yGrid = d3.axisLeft(yScale)
    .ticks(10)
    .tickSize(-plotWidth)   // deve essere negativo sull'asse X
    .tickFormat('');
}

function update() {
  updateScales();

  area = d3.area()
    .x(d => xScale(d.freq))
    .y0(yScale(0)) // ora è aggiornato ogni volta con la nuova scala
    .y1(d => yScale(d.gain))
    .curve(d3.curveMonotoneX);

  areaPath.datum(generateCurve()).attr("d", area);
  curvePath.datum(generateCurve()).attr("d", line);
  points.attr("cx", d => xScale(d.freq)).attr("cy", d => yScale(d.gain));

  axisX.attr("transform", `translate(0,${plotHeight})`).call(xAxis.scale(xScale));
  axisY.call(yAxis.scale(yScale));

  gridX.attr("transform", `translate(0,${plotHeight})`).call(xGrid.scale(xScale));
  gridY.call(yGrid.scale(yScale));


  g.select(".x-label").attr("x", plotWidth / 2).attr("y", plotHeight + 40);
  g.select(".y-label").attr("x", -plotHeight / 2).attr("y", -margin.left + 15);

  updateInputs();
}

function updateInputs() {
  d3.selectAll(".band").each(function(_, i) {
    const el = d3.select(this);
    el.select(".freq").property("value", bands[i].freq.toFixed(0));
    el.select(".gain").property("value", bands[i].gain.toFixed(1));
    if (i === 1 || i === 2) {
      el.select(".q").property("value", bands[i].q.toFixed(2));
    }
  });
}

const controlsDiv = d3.select(".controls");

function updateFromInputs() {
  d3.selectAll(".band").each(function(_, i) {
    const el = d3.select(this);
    let freq = +el.select(".freq").property("value");
    let gain = +el.select(".gain").property("value");
    let q = bands[i].q;
    const qInput = el.select(".q").node();
    if (qInput) {
      q = +qInput.value;
    } else {
      q = 0.8;
    }
    bands[i].freq = Math.min(20000, Math.max(20, freq));
    bands[i].gain = Math.min(15, Math.max(-15, gain));
    bands[i].q = Math.min(16, Math.max(0.36, q));
  });
  update();
}

d3.selectAll("input").on("input", updateFromInputs);

window.addEventListener("resize", update);

update();

// Funzione per abilitare scroll mouse su input per cambiare valore
function enableWheelAdjust(inputEl, bandIndex, key) {
  const step = {
    freq: 10,
    gain: 0.5,
    q: 0.05
  };
  inputEl.addEventListener("wheel", function(e) {
    e.preventDefault();
    let val = parseFloat(inputEl.value);
    val += (e.deltaY < 0 ? 1 : -1) * step[key];

    // Limiti
    if (key === "freq") val = Math.min(20000, Math.max(20, val));
    if (key === "gain") val = Math.min(15, Math.max(-15, val));
    if (key === "q") val = Math.min(16, Math.max(0.36, val));

    inputEl.value = key === "freq" ? val.toFixed(0) : val.toFixed(2);
    bands[bandIndex][key] = val;

    setEQ(bandIndex, key, val.toFixed(2));
    update();
  }, { passive: false });
}

// Funzione per abilitare drag touch orizzontale per cambiare valore input
function enableTouchScrubbing(inputEl, bandIndex, key) {
  let startX = 0;
  let startVal = 0;
  const sensitivity = {
    freq: 2,
    gain: 0.1,
    q: 0.05
  };

  inputEl.addEventListener("touchstart", function(e) {
    if (e.touches.length !== 1) return;
    const touch = e.touches[0];
    startX = touch.clientX;
    startVal = parseFloat(inputEl.value);
    e.preventDefault();
  });

  inputEl.addEventListener("touchmove", function(e) {
    if (e.touches.length !== 1) return;
    const touch = e.touches[0];
    const deltaX = touch.clientX - startX;
    let delta = deltaX * sensitivity[key];
    let newValue = startVal + delta;

    // Limiti
    if (key === "freq") newValue = Math.min(20000, Math.max(20, newValue));
    if (key === "gain") newValue = Math.min(15, Math.max(-15, newValue));
    if (key === "q") newValue = Math.min(16, Math.max(0.36, newValue));

    inputEl.value = key === "freq" ? newValue.toFixed(0) : newValue.toFixed(2);
    const parsed = parseFloat(inputEl.value);
    bands[bandIndex][key] = parsed;
    
    setEQ(bandIndex, key, parsed.toFixed(2));

    update();
    e.preventDefault();
  });

  inputEl.addEventListener("touchend", function(e) {
    startX = 0;
  });
}

// Attiva le due funzionalità su tutti gli input generati
d3.selectAll(".band").each(function(_, i) {
  const el = d3.select(this);
  enableWheelAdjust(el.select(".freq").node(), i, "freq");
  enableWheelAdjust(el.select(".gain").node(), i, "gain");
  if (el.select(".q").node()) {
    enableWheelAdjust(el.select(".q").node(), i, "q");
  }

  enableTouchScrubbing(el.select(".freq").node(), i, "freq");
  enableTouchScrubbing(el.select(".gain").node(), i, "gain");
  if (el.select(".q").node()) {
    enableTouchScrubbing(el.select(".q").node(), i, "q");
  }
});


function setEQ(banda, tipo, value){

    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./EQset");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
      channel : this.channel,
      typeFreq : banda,
      typeEq : tipo,
      value : value
    };

    xhttp.send(JSON.stringify(message));
}

function setEQSwitch(value){

    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./EQSwitch");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
      channel : this.channel,
      switch : value
    };

    xhttp.send(JSON.stringify(message));
}

let value_patch = -1

function openEq(channel, name){
  this.channel = channel
  document.getElementsByClassName('eq-container')[0].style.display='block'; 
  document.getElementsByClassName('first-line')[0].style.display='block'; 
  document.getElementById('channel-name').innerHTML=`CH ${channel} - ${name}`;

  const xhttp = new XMLHttpRequest();
  xhttp.open("GET", `/mixer/EQget/${channel}`);
  xhttp.send();
  //set loading
  spinner = document.getElementById("spinner");
  spinner.classList.remove("hidden-important"); 
  graph = document.getElementsByClassName("graph-container")[0];
  first_line = document.getElementsByClassName("first-line")[0];
  if (getComputedStyle(graph).display == "none")
      graph = "null"
  else
      graph.style.display ="None"

  if (getComputedStyle(first_line).display == "none")
      first_line = "null"
  else
      first_line.style.display ="None"


  xhttp.onload = function(){
      const obj = JSON.parse(this.responseText);
      const result = JSON.parse(obj)

      for (const [index, band] of result.entries()) {        
          bands[index]["gain"] = band.gain;

          bands[index]["freq"] = band.freq; 

          if(band.q){
              bands[index]["q"] = band.q; 
          }
      }

      spinner.classList.add("hidden-important"); 
      if(graph)
          graph.style.display ="block"

      update();
  }

  const xhttp2 = new XMLHttpRequest();
  xhttp2.open("GET", `/mixer/EQSwitch/${channel}`);
  xhttp2.send();

  xhttp2.onload = function(){
      const obj = JSON.parse(this.responseText);
      switchEQ = document.getElementById("switchEQ");
      if(switchEQ)
          switchEQ.checked = obj;
      
  }

  const xhttp3 = new XMLHttpRequest();
  xhttp3.open("GET", `/mixer/PreampGet/${channel}`);
  xhttp3.send();

  xhttp3.onload = function(){
    
      const json = JSON.parse(this.responseText);
      const obj = JSON.parse(json);

      slider = document.getElementById("pre-amp");
      gain_container = document.getElementById("gain-container");
      value_patch = parseInt(obj.ch_patch);
      if(value_patch == -1){
        gain_container.style.display = "none"
        if(slider){
          slider.value = 0
        }
      }
      else{
        gain_container.style.display = "flex"
        if(slider){
            slider.value=obj.preamp;
        }
      }      
      if(first_line)
          first_line.style.display ="flex"
  }
}


function setPreamp(value){

  if(value_patch != null && value_patch != -1){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", `/mixer/PreampSet`);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    request = {
        channel : value_patch,
        value : value
    };


    xhttp.send(JSON.stringify(request));
  }
}

function changeValueGain(type){
  const slider = document.getElementById("pre-amp");

  if(slider){
      value = parseInt(slider.value);
      switch(type){
        case "plus":
          value = Math.min(value + 1, 55);
          break;
        case "minus":
          value = Math.max(value - 1, 0);
          break;
      }

      slider.value = value;
      setPreamp(value);
  }
}