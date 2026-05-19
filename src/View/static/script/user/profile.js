

function openNav() {
    closeSaveNav();
    document.getElementById("profile-nav").style.width = "250px";
}

function closeNav() {
    document.getElementById("profile-nav").style.width = "0";
}


function openSaveNav() {
    closeNav();
    document.getElementById("profile-save-nav").style.width = "250px";
}

function closeSaveNav() {
    document.getElementById("profile-save-nav").style.width = "0";
}

function saveProfile(id) {
    closeSaveNav();
    if (spinner)
        spinner.hidden = false;
    const rawProfiles = getProfileChannelsValue();

    const profiles = Object.entries(rawProfiles).map(([key, value]) => ({
        channel: key,
        value: value
    }));

    const profile = {
        id: id,
        profiles: profiles
    };

    const xhttp = new XMLHttpRequest();
    xhttp.open("PUT", "./updateProfile");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");


    xhttp.onreadystatechange = () => {
        if (xhttp.readyState === XMLHttpRequest.DONE) {
            const status = xhttp.status;
            if (status === 0 || (status >= 200 && status < 400)) {
                const prof = document.getElementById(`profile_${id}`);
                loadProfile(id, prof.textContent.trim());

            } else {
                alert("errore");
            }
        }
        if (spinner)
            spinner.hidden = true;
    }

    xhttp.send(JSON.stringify(profile));

}

function saveNewProfile() {
    closeSaveNav();
    el = document.getElementById("name-profile");
    if (spinner)
        spinner.hidden = false;

    if (el) {
        if (el.value == null || el.value == "")
            alert("nome non inserito");
        else {
            const rawProfiles = getProfileChannelsValue();

            const profiles = Object.entries(rawProfiles).map(([key, value]) => ({
                channel: key,
                value: value
            }));

            const profile = {
                name: el.value,
                profiles: profiles
            };

            const xhttp = new XMLHttpRequest();
            xhttp.open("POST", "./createProfile");
            xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

            xhttp.onreadystatechange = () => {
                if (xhttp.readyState === XMLHttpRequest.DONE) {
                    const status = xhttp.status;
                    if (status === 0 || (status >= 200 && status < 400)) {

                        data = JSON.parse(xhttp.responseText);
                        profileRes = JSON.parse(data);

                        const id = profileRes.id;
                        const name = profileRes.name;
                        // aggiungo il profilo alla lista

                        const container = document.getElementById("profile-nav");
                        if (container) {
                            const a = document.createElement("a");
                            a.classList.add("profile-item");
                            a.id = `profile_${id}`;
                            a.href = "#";
                            a.onclick = () => { loadProfile(id, name); };
                            console.log(a.onclick);
                            a.innerHTML = name;

                            const i = document.createElement("i");
                            i.classList.add("bi", "bi-trash");
                            i.onclick = () => { event.stopPropagation(); deleteProfile(id); };
                            a.appendChild(i);

                            container.appendChild(a);


                            const containerSave = document.getElementById("profile-save-nav");
                            const inputContainer = document.getElementById("new-profile-div");

                            if (containerSave && inputContainer) {
                                const a2 = document.createElement("a");
                                a2.href = "#";
                                a2.id = `profile_save_${id}`;
                                a2.classList.add("profile-item");
                                a2.textContent = name;
                                a2.addEventListener("click", () => saveProfile(id, name));

                                // Inserisce a2 subito PRIMA di #new-profile-div
                                containerSave.insertBefore(a2, inputContainer);
                            }

                            document.querySelector("#name-profile").value = "";

                            loadProfile(profileRes.id, profileRes.name);

                        }

                    } else {
                        alert("errore");
                    }
                }

                if (spinner)
                    spinner.hidden = true;
            }

            xhttp.send(JSON.stringify(profile));
        }
    }
}

function loadProfile(id, name) {
    const xhttp = new XMLHttpRequest();

    const params = new URLSearchParams({
        profile_id: id
    });

    xhttp.open("GET", `./getProfile?${params.toString()}`);

    xhttp.onreadystatechange = () => {
        if (xhttp.readyState === XMLHttpRequest.DONE) {
            const status = xhttp.status;
            if (status === 0 || (status >= 200 && status < 400)) {

                const response = JSON.parse(xhttp.responseText);
                const responseJson = JSON.parse(response);

                if (responseJson != null) {
                    for (const key in responseJson) {
                        let element = document.getElementById("canale_" + key);
                        if (element != null)
                            element.value = parseInt(responseJson[key], 10);
                    }

                    closeNav();
                    document.getElementsByClassName("profile-name")[0].innerHTML = name;


                    // style
                    const profiles = document.getElementsByClassName("profile-item");

                    Array.from(profiles).forEach(p => {
                        p.classList.remove("selected");
                    });

                    profile = document.getElementById(`profile_${id}`);
                    if (profile) {
                        profile.classList.add("selected");
                    }
                }
            } else {
                alert("errore");
            }
        }
    }

    xhttp.send();
}

function getProfileChannelsValue() {
    let profile = {};

    let inputs = document.getElementsByClassName("inputRange");

    Array.from(inputs).forEach(element => {
        const match = element.id.match(/\d+$/);
        const numero = match ? match[0] : null;

        if (numero !== null) {
            profile[numero] = element.value;
        }
    });

    return profile;
}

function deleteProfiles() {
    if (confirm('Sei sicuro di voler eliminare tutti i profili?')) {
        const xhttp = new XMLHttpRequest();
        if (spinner)
            spinner.hidden = false;

        xhttp.open("DELETE", `./deleteProfiles`);

        xhttp.onreadystatechange = () => {
            if (xhttp.readyState === XMLHttpRequest.DONE) {
                const status = xhttp.status;
                if (status === 0 || (status >= 200 && status < 400)) {
                    const profiles = document.getElementsByClassName("profile-item");
                    Array.from(profiles).forEach(p => {
                        p.remove();
                    });

                    document.getElementsByClassName("profile-name")[0].innerHTML = "";
                } else {
                    alert("errore");
                }
            }
            if (spinner)
                spinner.hidden = true;
        }

        xhttp.send();
    }
}

function deleteProfile(id) {
    if (confirm('Sei sicuro di voler eliminare il profilo?')) {
        const xhttp = new XMLHttpRequest();
        if (spinner)
            spinner.hidden = false;

        const params = new URLSearchParams({
            profile_id: id
        });
        xhttp.open("DELETE", `./deleteProfile?${params.toString()}`);

        xhttp.onreadystatechange = () => {
            if (xhttp.readyState === XMLHttpRequest.DONE) {
                const status = xhttp.status;
                if (status === 0 || (status >= 200 && status < 400)) {

                    const prof = document.getElementById(`profile_${id}`);
                    if (prof)
                        prof.remove();

                    const prof_save = document.getElementById(`profile_save_${id}`);
                    if (prof_save)
                        prof_save.remove();

                } else {
                    alert("errore");
                }
            }
            if (spinner)
                spinner.hidden = true;
        }
        xhttp.send();
    }
}