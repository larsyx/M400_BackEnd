let aux_id_selected = -1;

function openAuxs(){
    const sceneContainer = document.querySelector(".aux-container");
    sceneContainer.classList.add("visible");
    if(aux_id_selected !== -1){
        loadAuxParameters(aux_id_selected);
    }
}

function closeAuxs(){
    const sceneContainer = document.querySelector(".aux-container");
    sceneContainer.classList.remove("visible");
    closeSocketAux();
}

function loadAuxParameters(aux_id){

    closeSocketAux();
    aux_id_selected = aux_id;
    const spinner = document.getElementById("aux_spinner");
    const aux_channels_el = document.getElementById("aux-channels-id");
    
    if(spinner)
        spinner.classList.remove("hidden-important"); 
    if(aux_channels_el)
        aux_channels_el.classList.add("hidden-important");
    
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", `./aux/get/${aux_id}`);
    xhttp.setRequestHeader("Content-Type", "application/json");

    xhttp.onload = function() {
        if (xhttp.status === 200) {
            const aux_channels = JSON.parse(xhttp.responseText);
            const aux_channels_json = JSON.parse(aux_channels);
            const aux_channels_list = aux_channels_json["channels"];
            const aux_switch = aux_channels_json["switch"]

            for (const [chiave, valore] of Object.entries(aux_channels_list)) {
                const element = document.getElementById(`aux_canale_${chiave}`);
                if (element) {
                    element.value = valore;
                }
            }

            const element = document.getElementById('aux_switch_main');
            if(element)
                element.checked = aux_switch;


            
            spinner.classList.add("hidden-important");
            if (aux_channels_el) 
                aux_channels_el.classList.remove("hidden-important");
            
            
        } else {
            console.error("Failed to load aux parameters:", xhttp.statusText);
        }
    }

    xhttp.send();

    openAndSetSocket();
}

function sendMessageAux(canaleId, value) {
    if(aux_id_selected !== -1){
        const xhttp = new XMLHttpRequest();
        xhttp.open("POST", "./aux/set", true)
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

        const message = {
            auxId : aux_id_selected,
            canaleId: canaleId,
            value: value
        };

        xhttp.send(JSON.stringify(message));
    }
}

function checkSwitchAux(canaleId, value) {
    if(aux_id_selected !== -1){
        const xhttp = new XMLHttpRequest();
        xhttp.open("POST", "./aux/switch/set", true)
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

        const message = {
            auxId : aux_id_selected,
            canaleId: canaleId,
            value: value
        };

        xhttp.send(JSON.stringify(message));
    }
}


function changeValueAux(canaleId, action){
    
    inputRange = document.getElementById("aux_canale_"+canaleId);
    let value = parseInt(inputRange.value, 10);

    if(action == "plus")
        value = Math.min(value + step, 100);
    else if(action == "minus")
        value = Math.max(value - step, 0);
    inputRange.value = value;


    sendMessageAux(canaleId, value);

}

let socket_aux;

function openAndSetSocket(){
    socket_aux = new WebSocket(`wss://${window.location.host}/ws/liveMixerSync/aux/${aux_id_selected}`);

    socket_aux.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const type = data.type
        const canaleId = data.channel;
        const value = data.value;
        if(type === "fader"){
            const inputElement = document.getElementById(`aux_canale_${canaleId}`);
            if (inputElement) {
                inputElement.value = value;
            }
        }
        else if(type === "switch"){
            const inputElement = document.getElementById(`aux_switch_${canaleId}`);
            if (inputElement) {
                inputElement.checked = value;
            }
        }
        
    };


}

function closeSocketAux() {
    if(aux_id_selected !== -1)
        socket_aux.close();
}