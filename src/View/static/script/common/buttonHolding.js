function enableHoldClick(button) {
    let interval;
    let isTouch = false;

    const triggerClick = () => {
        if (typeof button.onclick === 'function') {
            button.onclick();
        } else {
            button.dispatchEvent(new Event('click'));
        }
    };

    const startClicking = () => {
        triggerClick(); 
        interval = setInterval(triggerClick, 200);
    };

    const stopClicking = () => {
        clearInterval(interval);
        interval = null;
    };

    button.addEventListener('touchstart', e => {
        isTouch = true;
        e.preventDefault(); 
        if (!interval) startClicking();
    });

    button.addEventListener('touchend', stopClicking);
    button.addEventListener('touchcancel', stopClicking);

}

const sliders = document.getElementsByClassName('canale-container'); 

for (const slider of sliders) {
    const btns = slider.querySelectorAll('button[onclick]');
    btns.forEach(enableHoldClick);
}

const aux_containers = document.getElementsByClassName('aux-channels-container'); 

for (const aux of aux_containers) {
    const btns = aux.querySelectorAll('button[onclick]');
    btns.forEach(enableHoldClick);
}

const main = document.getElementsByClassName('main-fader')[0]; 
if(main){
    let btns = main.querySelectorAll('button[onclick]');
    btns.forEach(enableHoldClick);
}
const drumButton = document.getElementsByClassName('drum')[0];
if(drumButton){
    btns = drumButton.querySelectorAll('button[onclick]');
    btns.forEach(enableHoldClick);
}

const gain = document.getElementById('gain-container');
if(gain){
    btns = gain.querySelectorAll('button[onclick]');
    btns.forEach(enableHoldClick);
}


function isVertical(slider) {
    const rect = slider.getBoundingClientRect();
    return rect.height > rect.width;
}

function isClickOnThumb(e) {
    const slider = e.currentTarget;
    const rect = slider.getBoundingClientRect();
    const sliderValue = parseFloat(slider.value);
    const min = parseFloat(slider.min || 0);
    const max = parseFloat(slider.max || 100);
    const valueRatio = (sliderValue - min) / (max - min);

    const thumbSize = 30;

    if (isVertical(slider)) {
        const y = e.clientY || (e.touches && e.touches[0].clientY);
        const thumbY = rect.bottom - rect.height * valueRatio;
        return Math.abs(y - thumbY) < thumbSize;
    } else {
        const x = e.clientX || (e.touches && e.touches[0].clientX);
        const thumbX = rect.left + rect.width * valueRatio;
        return Math.abs(x - thumbX) < thumbSize;
    }
}

function enableCustomSlider(slider) {
  let startX = null;
  let startY = null;
  let startValue = null;
  let dragging = false;
  let vertical = isVertical(slider);
  let min = Number(slider.min) || 0;
  let max = Number(slider.max) || 100;
  let step = Number(slider.step) || 1;
  let range = max - min;

  function getCoord(e) {
    return {
      x: e.clientX,
      y: e.clientY
    };
  }

  slider.addEventListener("pointerdown", (e) => {
    if (!isClickOnThumb(e)) {
      e.preventDefault();
      e.stopPropagation();
    }

    const { x, y } = getCoord(e);
    startX = x;
    startY = y;
    startValue = Number(slider.value);
    dragging = false;
    slider.setPointerCapture(e.pointerId);
  });

  slider.addEventListener("pointermove", (e) => {
    if (!slider.hasPointerCapture(e.pointerId)) return;

    const { x, y } = getCoord(e);
    const deltaX = x - startX;
    const deltaY = y - startY;

    if (!dragging) {
      // decido la direzione solo dopo che l'utente si è mosso un po'
      if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
        if (vertical && Math.abs(deltaY) > Math.abs(deltaX)) {
          dragging = true; // verticale: movimento prevalente in Y
        } else if (!vertical && Math.abs(deltaX) > Math.abs(deltaY)) {
          dragging = true; // orizzontale: movimento prevalente in X
        } else {
          // gesto è scroll → rilascio il capture e lascio scorrere
          slider.releasePointerCapture(e.pointerId);
          return;
        }
      } else {
        return; // non ancora deciso
      }
    }

    e.preventDefault(); // blocco lo scroll SOLO quando sono in drag

    const sliderSize = vertical ? slider.offsetHeight : slider.offsetWidth;
    const delta = vertical ? -deltaY : deltaX;
    const percent = delta / sliderSize;

    let newValue = startValue + percent * range;
    newValue = Math.round(newValue / step) * step;
    newValue = Math.max(min, Math.min(max, newValue));

    slider.value = newValue;
    slider.dispatchEvent(new InputEvent("input", { bubbles: true }));
  });

  slider.addEventListener("pointerup", (e) => {
    if (slider.hasPointerCapture(e.pointerId)) {
      slider.releasePointerCapture(e.pointerId);
    }
    dragging = false;
  });

  slider.addEventListener("pointercancel", () => {
    dragging = false;
  });
}

// Attivazione su tutti gli slider
document.querySelectorAll('input[type="range"]').forEach(enableCustomSlider);


window.addEventListener("offline", () => {
  alert("Connessione persa!\nConnettiti alla rete Wi-Fi del mixer per continuare a usarlo.");
});
