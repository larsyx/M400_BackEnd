function sendMessage(canaleId, value) {
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./set", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        canaleId: canaleId,
        value: value,
        aux: aux
    };

    xhttp.send(JSON.stringify(message));
}

function sendMessageMain(value) {
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./set/main", true)
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const message = {
        value: value,
        aux: auxMain
    };

    xhttp.send(JSON.stringify(message));
}

function changeValue(canaleId, action) {
    inputRange = document.getElementById("canale_" + canaleId);
    let value = parseInt(inputRange.value, 10);

    if (action == "plus")
        value = Math.min(value + step, 100);
    else if (action == "minus")
        value = Math.max(value - step, 0);
    inputRange.value = value;

    if (canaleId == "main")
        sendMessageMain(value);
    else
        sendMessage(canaleId, value);
}

function changeDrum(action) {
    inputsRange = document.getElementsByClassName("batteria");

    for (const input of inputsRange) {
        let value = parseInt(input.value, 10);
        if (action == "plus")
            value = Math.min(value + step, 100);
        else if (action == "minus")
            value = Math.max(value - step, 0);
        input.value = value;


        id = input.id.split("_")
        canaleId = id[1]
        sendMessage(canaleId, value);
    }
}

let socket;
let isConneting = false;
const spinner = document.getElementById("spinner-container");


function syncFader() {
    if (spinner)
        spinner.hidden = false;
    const params = new URLSearchParams({
        aux: aux,
        auxMain: auxMain
    });
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", `./getFadersValue?${params.toString()}`);
    xhttp.send();

    xhttp.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 200) {
                try {
                    const response = JSON.parse(this.responseText);
                    const responseJson = typeof response === "string" ? JSON.parse(response) : response;
                    if (responseJson != null) {
                        for (const key in responseJson) {
                            let element = document.getElementById("canale_" + key);
                            if (element != null)
                                element.value = parseInt(responseJson[key], 10);
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

function toggleNames() {
    const button = document.getElementById("toggleNamesButton");

    if (button.innerHTML === "Nomi mixer") {
        syncNames();
    }
    else {
        setDefaultNames();
    }

    button.innerHTML = button.innerHTML === "Nomi mixer" ? "Nomi personalizzati" : "Nomi mixer";

}

function syncNames() {
    fetch(`./getNamesValue`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            list_channels: canali.map(c => c.id)
        })
    })
        .then(response => response.json())
        .then(data => {

            Object.entries(data).forEach(([key, value]) => {
                document.getElementById("descrizione_" + key).innerText = value;
            });

        });
}

function setDefaultNames() {
    canali.forEach(canale => {
        document.getElementById("descrizione_" + canale.id).innerText = canale.name;
    });
}

const aux_items = document.querySelectorAll('.aux-item');
const aux_button = document.querySelector('.aux_button');

aux_items.forEach(item => {

    item.addEventListener('click', (e) => {
        const id = e.target.id.split("_")[1];
        fetch(`./getAux/${id}`, {
            method: 'GET'
        })
            .then(response => response.json())
            .then(data => {
                aux_items.forEach(i => i.classList.remove('active'));
                e.target.classList.add('active');

                aux_button.textContent = e.target.textContent;

                aux = data.midi_address;
                auxMain = data.midi_address_main;

                syncFader();
                socket.close();
                createAndConnectWebSocket();
            });
    });
});

// WebSocket connection
function createAndConnectWebSocket() {

    if (socket && socket.readyState === WebSocket.OPEN) {
        return;
    }

    if (socket && socket.readyState === WebSocket.CONNECTING) {
        socket.close();
    }


    isConnecting = true;

    syncFader();

    socket = new WebSocket(`wss://${window.location.host}/ws/liveSync`);

    socket.onopen = function () {
        message = {
            "address": aux,
            "addressMain": auxMain
        }
        socket.send(JSON.stringify(message));

        message = document.querySelector(".alert");
        message.hidden = true;
    };

    socket.onmessage = function (event) {
        const response = JSON.parse(event.data);
        if (response != null) {
            let element = null;
            element = document.getElementById("canale_" + response.channel);
            if (element != null)
                element.value = response.value;

        }
    };

    socket.onerror = function (error) {
        isConnecting = false;
        message = document.querySelector(".alert");
        if (message) {
            message.hidden = false;
            message.getElementsByTagName("p")[0].innerHTML = "Errore sincronizzazione: " + error.message;
        }
    };

    socket.onclose = function (e) {
        isConnecting = false;
        message = document.querySelector(".alert");
        message.hidden = false;
        message.getElementsByTagName("p")[0].innerHTML = "Disconnesso, nessuna sincronizzazione con il mixer <a href='#' onclick='createAndConnectWebSocket();'>ricarica la pagina</a>";

        setTimeout(createAndConnectWebSocket, 1000);
    };
}


function ensureWebSocket() {
    if (!socket || socket.readyState === WebSocket.CLOSED || socket.readyState === WebSocket.CLOSING) {
        createAndConnectWebSocket();
    }
}


document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        ensureWebSocket();
    }
});

window.addEventListener("focus", ensureWebSocket);
window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        ensureWebSocket();
    }
});

createAndConnectWebSocket();

setInterval(ensureWebSocket, 5000);



function toggleMain() {
    const lateral = document.querySelector(".lateral");
    const container = document.querySelector(".container");

    // Solo su schermi piccoli
    if (window.innerWidth <= 500) {
        if (lateral.classList.contains("show")) {
            lateral.classList.remove("show");
            container.classList.remove("shifted");
        } else {
            lateral.classList.add("show");
            container.classList.add("shifted");
        }
    }
}


const dropdownElement = document.getElementById('menu');
const canvas = document.getElementsByClassName('sticky')[0];

dropdownElement.addEventListener('show.bs.dropdown', () => {
    canvas.style.zIndex = '-1';
});

dropdownElement.addEventListener('hide.bs.dropdown', () => {
    canvas.style.zIndex = '0';
});