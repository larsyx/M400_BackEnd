function switchLayout() {
    const link = document.getElementById('layout-style');
    const currentHref = link.getAttribute('href');

    if (currentHref.includes('/static/style/mixer/horizontal-layout.css')) {
        link.setAttribute('href', '/static/style/mixer/vertical-layout.css');
    } else {
        link.setAttribute('href', '/static/style/mixer/horizontal-layout.css');
    }
}


function sendMessage(canaleId, value) {
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./set", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
            canaleId: canaleId,
            value: value
    };

    xhttp.send(JSON.stringify(message));
}

function sendMessageMain(value){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./set/main", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
            value: value,
    };

    xhttp.send(JSON.stringify(message));
}

function changeValue(canaleId, action){
    inputRange = document.getElementById("canale_"+canaleId);
    let value = parseInt(inputRange.value, 10);

    if(action == "plus")
        value = Math.min(value + step, 100);
    else if(action == "minus")
        value = Math.max(value - step, 0);
    inputRange.value = value;

    if(canaleId == "main")
        sendMessageMain(value);
    else
        sendMessage(canaleId, value);
}

function checkSwitch(canaleId, switchValue){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./switch", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        canaleId: canaleId,
        switch: switchValue
    };

    xhttp.send(JSON.stringify(message));
}

function checkSwitchMain(switchValue){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./switch/main", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        switch: switchValue
    };

    xhttp.send(JSON.stringify(message));
}

let socket;
let isConneting = false;
const spinner = document.getElementById("spinner-container");


function syncFader(){
    if(spinner)
        spinner.hidden = false;

    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", `./getFadersValue`);
    xhttp.send();

    xhttp.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 200) {
                try {
                    const response = JSON.parse(this.responseText);
                    const responseJson = typeof response === "string" ? JSON.parse(response) : response;
                    if (responseJson != null) {
                        for (const key in responseJson) {
                            let element;
                            if(key == 'switch'){
                                element = document.getElementById("switch_main");
                                if(element != null)
                                    element.checked = responseJson[key];   
                            }else{
                                element = document.getElementById("canale_" + key);
                                if (element != null)
                                    element.value = parseInt(responseJson[key], 10);
                            }
                        }
                    }
                } catch (e) {
                    console.error("Errore nel parsing JSON:", e);
                }
            } else {
                console.warn("Errore nella richiesta:", this.status, this.statusText);
            }

            if (spinner)
                spinner.hidden = true;
        }
    }
}

// WebSocket connection
function createAndConnectWebSocket(){
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING || isConnecting)) {
        return;
    }

    isConnecting = true;

    syncFader();

    socket = new WebSocket(`wss://${window.location.host}/ws/liveSyncVideo`); 

    socket.onopen = function(){
        message = document.querySelector(".alert");
        message.hidden = true;
    };

    socket.onmessage = function(event){
        const response = JSON.parse(event.data);
        if(response != null){
            let elname = "";

            let element = null;
            if(response.type === "switch"){
                element = document.getElementById(elname+"switch_"+response.channel);
                if(element != null){
                    element.checked = response.value;
                }
            }else if(response.type === "fader"){
                element = document.getElementById(elname+"canale_"+response.channel);
                if(element != null)
                    element.value = response.value;
            }

        }
    };

    socket.onerror = function(error){
        isConnecting = false;
        message = document.querySelector(".alert");
        message.hidden = false;
        message.getElementsByTagName("p")[0].innerHTML = "Errore sincronizzazione: " + error.message;
    };

    socket.onclose = function(e){
        isConnecting = false;
        message = document.querySelector(".alert");
        message.hidden = false;
        message.getElementsByTagName("p")[0].innerHTML = "Disconnesso, nessuna sincronizzazione con il mixer <a href='#' onclick='createAndConnectWebSocket();'>ricarica la pagina</a>";

    };
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    createAndConnectWebSocket();
  }
});

window.addEventListener("focus", () => {
  createAndConnectWebSocket();
});

window.addEventListener("pageshow", (event) => {
    if (event.persisted || socket.readyState !== WebSocket.OPEN) {
        createAndConnectWebSocket();
    }
});

createAndConnectWebSocket();


document.addEventListener("DOMContentLoaded", function () {
    const buttonContainer = document.getElementById("scene-button");
    if (!buttonContainer) return;

    const button = buttonContainer.querySelector("button[type='menu']");
    if (!button) return;

    button.addEventListener("click", function () {
        const sceneContainer = document.querySelector(".scene-container-list");
        if (sceneContainer)
            sceneContainer.classList.toggle("visible");
    });
});