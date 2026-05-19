function switchLayout() {
    const link = document.getElementById('layout-style');
    const currentHref = link.getAttribute('href');

    if (currentHref.includes('/static/style/mixer/horizontal-layout.css')) {
        link.setAttribute('href', '/static/style/mixer/vertical-layout.css');
    } else {
        link.setAttribute('href', '/static/style/mixer/horizontal-layout.css');
    }
}

function sendMessageDca(dca_id, value){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./set/dca", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
            dca_id: dca_id,
            value: value
    };

    xhttp.send(JSON.stringify(message));
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

function changeValue(canaleId, action, type){
    if(type == "dca")
        inputRange = document.getElementById("dca_canale_"+canaleId);
    else
        inputRange = document.getElementById("canale_"+canaleId);
    let value = parseInt(inputRange.value, 10);

    if(action == "plus")
        value = Math.min(value + step, 100);
    else if(action == "minus")
        value = Math.max(value - step, 0);
    inputRange.value = value;

    if(type == "dca")
        sendMessageDca(canaleId, value);
    else if(canaleId == "main")
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


function checkSwitchDca(dca_id, switchValue){
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./switch/dca", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        dca_id: dca_id,
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


const socket = new WebSocket(`wss://${window.location.host}/ws/liveSyncMixer`); 

socket.onopen = function(){};

socket.onmessage = function(event){
    const response = JSON.parse(event.data);
    if(response != null){
        let elname = "";
        if(response.dca)
            elname = "dca_";

        let element = null;
        if(response.type === "switch")
            element = document.getElementById(elname+"switch_"+response.channel);
            if(element != null)
                element.checked = response.value;
        else if(response.type === "fader")
            element = document.getElementById(elname+"canale_"+response.channel);
            if(element != null)
                element.value = response.value;

    }
};

socket.onerror = function(error){
    message = document.querySelector(".alert");
    message.hidden = false;
    message.getElementsByTagName("p")[0].innerHTML = "Errore sincronizzazione: " + error.message;
};

socket.onclose = function(e){
    message = document.querySelector(".alert");
    message.hidden = false;
    message.getElementsByTagName("p")[0].innerHTML = "Disconnesso, nessuna sincronizzazione con il mixer <a href='./home'>ricarica la pagina</a>";

};

function openScene(){
    const sceneContainer = document.querySelector(".scene-container-list");
    sceneContainer.classList.toggle("visible");
}


// Disposition

function openDisposition(){
    const dispositionContainer = document.querySelector(".disposition-container");
    dispositionContainer.classList.toggle("visible");
}

const sortable =new Sortable(document.getElementById("sortable-element"), {
    animation: 150,
    handle: ".drag",
    dataIdAttr: "id"
});
const list = document.getElementById("sortable-element")

let draggedItem = null;


function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('li:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
        } else {
        return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function saveDisposition() {
    const ul = document.getElementById("sortable-element");
    const items = ul.querySelectorAll("li");

    const order = Array.from(items).map(item => item.id);

    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./saveDisposition", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        disposition: order
    };

    xhttp.send(JSON.stringify(message));

    xhttp.onload = function() {
        if (xhttp.status === 200) {
            window.location.reload();
        } else {
            alert("Errore nel salvataggio della disposizione");
        }
    };
}

function resetOrder(){
    const ul = document.getElementById("sortable-element");
    const items = ul.querySelectorAll("li");

    const ids = Array.from(items).map(li => li.id);

    const sortedIds = ids.sort((a, b) => Number(a) - Number(b));

    sortable.sort(sortedIds, true);
}