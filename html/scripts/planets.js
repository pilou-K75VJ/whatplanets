(function() {

// Canvas
const ctx = document.querySelector('#clock').getContext('2d');
ctx.translate(320, 320);  // Translate to center

// Images
const earth = document.querySelector("#clock #earth");
const earthBlurred = document.querySelector("#clock #earth-blurred");

// Speed buttons
const b7 = document.querySelector('#speed-buttons #b7');
const b6 = document.querySelector('#speed-buttons #b6');
const b5 = document.querySelector('#speed-buttons #b5');
const b4 = document.querySelector('#speed-buttons #b4');
const f0 = document.querySelector('#speed-buttons #f0');
const f4 = document.querySelector('#speed-buttons #f4');
const f5 = document.querySelector('#speed-buttons #f5');
const f6 = document.querySelector('#speed-buttons #f6');
const f7 = document.querySelector('#speed-buttons #f7');

// Jump
const jumpDate = document.querySelector('#jump #jump-date');
const jumpNow = document.querySelector('#jump #jump-now');

FPS = 50;

const colors = {
  'sun': '#ffd400',
  'moon': '#f7f7f7',

  'mercury': '#7f7f7f',
  'venus': '#afafaf',
  'mars': '#893400',
  'jupiter': '#89632a',
  'saturn': '#56451a',
  'uranus': '#5580aa',
  'neptune': '#366896',

  'vesta': '#404040',
  'iris': '#404040',
  'ceres': '#404040',
  'pallas': '#404040'
};

// Load database index
let indexDB;
(function() {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', 'data/full/index.json', true);
  xhr.responseType = 'json';
  xhr.onload = function(e) {
    if (this.status == 200) {
      indexDB = this.response;
    }
  };
  xhr.send();
})();

function date2YMD(date) {
  let d = new Date(date);
  return d.getUTCFullYear().toString().padStart(4, '0')  // year
         + (d.getUTCMonth() + 1).toString().padStart(2, '0')  // month
         + d.getUTCDate().toString().padStart(2, '0');  // day
}
function YMD2Date(ymd) {
  return Date.UTC(parseInt(ymd.slice(0, 4)),  // year
                  parseInt(ymd.slice(4, 6)) - 1,  // month
                  parseInt(ymd.slice(6, 8)));  // day
}

class Database {
  constructor(name, body, load = false) {
    this.name = name;
    this.body = body;
    this.jsonPath = `data/${name}/${body}.json`;

    this.content;
    this.requested = false;
    this.loaded = false;
    if (load) { this.loadData(); }
  }

  get data() {
    if (!this.requested) { this.loadData(); }
    if (!this.loaded) { return; }
    return this.content;
  }

  loadData() {
    if (this.requested) { return; }
    this.requested = true;

    // Get JSON content
    const xhr = new XMLHttpRequest();
    xhr.open('GET', this.jsonPath, true);
    xhr.responseType = 'json';
    let self = this;
    xhr.onload = function(e) {
      if (this.status == 200) {
        self.content = this.response;
        self.loaded = true;
      }
    };
    xhr.send();
  }
}

class Interpolator {
  constructor(body) {
    this.body = body;
    this.DB = {'lite': new Database('lite', body, true)};
    this.current = 'lite';

    this.loadedDB = false;
    this.outOfBounds = false;
    this.waiting = true;

    this.lon1;
    this.lon2;
    this.date1;
    this.date2;
    this.span;
  }

  changeCurrentDatabase(date) {
    if (!this.loadedDB) {
      if (indexDB === undefined) {
        this.current = undefined;
        return;
      } else {
        indexDB[this.body].forEach((name) => { this.DB[name] = new Database(`full/${name}`, this.body, false); })
        this.loadedDB = true;
      }
    }

    let year = (new Date(date)).getUTCFullYear();
    let current;
    if (
      Object.keys(this.DB).some((name) => {
        if (name == 'lite') { return false; }
        current = name;
        let [start, stop] = name.split('-');
        return (parseInt(start) <= year && parseInt(stop) >= year);
      })
    ) {
      this.current = current;
    } else {
      this.current = undefined;
    }
  }

  updateSpan(date) {
    this.waiting = !this.DB[this.current].loaded;
    if (this.waiting) {
      this.DB[this.current].loadData();
      return;
    }

    let d;

    this.date1 = undefined;
    for (let days=0; days<60; days++) {
      d = date2YMD(date - days * 86400000);
      if (this.DB[this.current].data.hasOwnProperty(d)) {
        this.lon1 = this.DB[this.current].data[d];
        this.date1 = YMD2Date(d);
        break;
      }
    }

    this.date2 = undefined;
    for (let days=1; days<60; days++) {
      d = date2YMD(date + days * 86400000);
      if (this.DB[this.current].data.hasOwnProperty(d)) {
        this.lon2 = this.DB[this.current].data[d];
        this.date2 = YMD2Date(d);
        break;
      }
    }

    if (this.lon1 - this.lon2 > Math.PI) {
      this.lon2 += 2 * Math.PI;
    } else if (this.lon2 - this.lon1 > Math.PI) {
      this.lon1 += 2 * Math.PI;
    }
    this.span = this.date2 - this.date1;

    this.outOfBounds = (this.date1 === undefined || this.date2 === undefined);
    if (this.outOfBounds) {
      this.changeCurrentDatabase(date);
      return;
    }
  }

  longitude(date) {
    if (this.waiting || this.outOfBounds) {
      this.updateSpan(date);
      return;
    } else if (date < this.date1 || date > this.date2) {
      this.updateSpan(date);
    }
    let x = (date - this.date1) / this.span;
    return -(this.lon1 * (1 - x) + this.lon2 * x);
  }
}

const sun = new Interpolator('sun');
const moon = new Interpolator('moon');

const mercury = new Interpolator('mercury');
const venus = new Interpolator('venus');
const mars = new Interpolator('mars');
const jupiter = new Interpolator('jupiter');
const saturn = new Interpolator('saturn');
const uranus = new Interpolator('uranus');
const neptune = new Interpolator('neptune');

const vesta = new Interpolator('vesta');
const iris = new Interpolator('iris');
const ceres = new Interpolator('ceres');
const pallas = new Interpolator('pallas');

function drawHand(color, angle) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(300 * Math.cos(angle), 300 * Math.sin(angle));
  ctx.stroke();
}

function drawDisk(color, radius) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(0, 0, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function drawEarth(date, sunLongitude, blurred) {
  let d = new Date(date);
  let angle = sunLongitude - Math.PI * (1 + (
                3600 * d.getUTCHours()
                + 60 * d.getUTCMinutes()
                + d.getUTCSeconds()
              ) / 43200);
  ctx.rotate(angle);
  if (blurred) {
   ctx.drawImage(earthBlurred, -120, -120, 240, 240);
  } else {
   ctx.drawImage(earth, -120, -120, 240, 240);
  }
  ctx.rotate(-angle);
}

let offset = 0;
let targetOffset = 0;
let speed = 1;
let targetSpeed = 1;
let date = Date.now();
let dt;

function updateOffset() {
  if (offset == targetOffset) {
    return;
  } else if (Math.abs((targetOffset - offset) / (date + targetOffset)) < 1E-7) {
    offset = targetOffset;
  } else {
    offset += (targetOffset - offset) / 5;
  }
}
function setDate(d) {
  speed = 1;
  targetSpeed = speed;
  offset = date - Date.now();
  switch (d) {
    case 'now': targetOffset = 0; break;
    case 'input': targetOffset = jumpDate.valueAsNumber - Date.now(); break;
  }
}

function updateSpeed() {
  if (speed == targetSpeed) {
    return;
  } else if (Math.abs((targetSpeed - speed) / targetSpeed) < 1E-3) {
    speed = targetSpeed;
  } else {
    speed += (targetSpeed - speed) / 5;
  }
  offset = date - speed * Date.now();
  targetOffset = offset;
}
function setSpeed(x) {
  targetSpeed = x;
}

jumpDate.oninput = function() { setDate('input'); }
jumpNow.onclick = function() { setDate('now'); }

b7.onclick = function() { setSpeed(-1E7); }
b6.onclick = function() { setSpeed(-1E6); }
b5.onclick = function() { setSpeed(-1E5); }
b4.onclick = function() { setSpeed(-1E4); }
f0.onclick = function() { setSpeed(1); }
f4.onclick = function() { setSpeed(1E4); }
f5.onclick = function() { setSpeed(1E5); }
f6.onclick = function() { setSpeed(1E6); }
f7.onclick = function() { setSpeed(1E7); }

function updateClock() {
  dt = speed * Date.now() + offset - date;
  date += dt;
  updateOffset();
  updateSpeed();
  jumpDate.valueAsNumber = date;

  ctx.clearRect(-320, -320, 640, 640);
  ctx.globalAlpha = 0.6;
  drawDisk('black', 310);

  ctx.globalAlpha = 0.8;
  ctx.lineCap = 'round';
  sunLongitude = sun.longitude(date);

  drawHand(colors.sun, sunLongitude);
  if (Math.abs(dt * FPS / 1000) < 5000000) {
    drawHand(colors.moon, moon.longitude(date));
  }

  drawHand(colors.mercury, mercury.longitude(date));
  drawHand(colors.venus, venus.longitude(date));
  drawHand(colors.mars, mars.longitude(date));
  drawHand(colors.jupiter, jupiter.longitude(date));
  drawHand(colors.saturn, saturn.longitude(date));
  drawHand(colors.uranus, neptune.longitude(date));
  drawHand(colors.neptune, uranus.longitude(date));

  drawHand(colors.vesta, vesta.longitude(date));
  drawHand(colors.iris, iris.longitude(date));
  drawHand(colors.ceres, ceres.longitude(date));
  drawHand(colors.pallas, pallas.longitude(date));

  ctx.globalAlpha = 1;
  if (Math.abs(dt * FPS / 1000) < 500000) {
    drawEarth(date, sunLongitude, blurred = false);
  } else {
//    drawDisk('#100f47', 105);
    drawEarth(date, sunLongitude, blurred = true);
  }
}

updateClock();
setInterval(updateClock, 1000 / FPS);

})();
