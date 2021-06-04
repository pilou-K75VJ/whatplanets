const ctx = document.getElementById('planets').getContext('2d');
ctx.translate(250, 250);  // Translate to center

const plColors = {
  sun: '#ffd400',
  mer: '#7f7f7f',
  ven: '#afafaf',
  lun: '#f7f7f7',
  mar: '#893400',
  jup: '#89632a',
  sat: '#56451a',
};

function drawHand(color, angle) {
  ctx.globalAlpha = 0.8;
  ctx.strokeStyle = color;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(200 * Math.cos(angle), 200 * Math.sin(angle));
  ctx.stroke();
}

function drawDisk(color, radius, alpha = 1) {
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(0, 0, radius, 0, 2 * Math.PI);
  ctx.fill();
}

function getDataRange(csvPath, date) {
  // Get raw CSV content
  let rawFile = new XMLHttpRequest();
  let txt = 'null';
  rawFile.open('GET', csvPath, false);
  rawFile.onreadystatechange = function () {
    if (rawFile.readyState === 4) {
      if (rawFile.status === 200 || rawFile.status == 0) {
        txt = rawFile.responseText;
      }
    }
  }
  rawFile.send(null);

  //Extract 'last' and 'next' rows
  let rows = txt.split('\n');
  let nRows = rows.length;
  let nextIndex = -1;
  rows.some(function(row) {
    nextIndex += 1;
    if (nextIndex === 0) { return false; }
    return Date.UTC(
      parseInt(row.slice(0, 4)),  // year
      parseInt(row.slice(5, 7)) - 1,  // month
      parseInt(row.slice(8, 10))  // day
    ) > date;  // Exit loop when (row date > considered date)
  });

  let row1 = rows[nextIndex - 1];
  let lon1 = parseFloat(row1.split(',')[1]);  // Ecliptic longitude
  let date1 = Date.UTC(
    parseInt(row1.slice(0, 4)),  // year
    parseInt(row1.slice(5, 7)) - 1,  // month
    parseInt(row1.slice(8, 10))  // day
  );

  let row2 = rows[nextIndex];
  let lon2 = parseFloat(row2.split(',')[1]);  // Ecliptic longitude
  let date2 = Date.UTC(
    parseInt(row2.slice(0, 4)),  // year
    parseInt(row2.slice(5, 7)) - 1,  // month
    parseInt(row2.slice(8, 10))  // day
  );

  let x = (date - date1) / (date2 - date1);
//  test.textContent += date1 + '___' + date2 + '___' + x + '__________\n';
  return -(lon1 * (1 - x) + lon2 * x);
}


function drawClock(sun, mer, ven,
                   lun, mar, jup, sat) {
  ctx.clearRect(-250, -250, 500, 500);
  drawDisk('black', 220, alpha=0.6);

  ctx.lineCap = 'round';
  drawHand(plColors.sun, sun);
  drawHand(plColors.mer, mer);
  drawHand(plColors.ven, ven);
  drawHand(plColors.lun, lun);
  drawHand(plColors.mar, mar);
  drawHand(plColors.jup, jup);
  drawHand(plColors.sat, sat);

  drawDisk('white', 20);
}

let test = document.querySelector('#test');

function updateClock() {
  let now = new Date();

  drawClock(
    getDataRange('data/sun.csv', now),
    getDataRange('data/mercury.csv', now),
    getDataRange('data/venus.csv', now),
    getDataRange('data/moon.csv', now),
    getDataRange('data/mars.csv', now),
    getDataRange('data/jupiter.csv', now),
    getDataRange('data/saturn.csv', now),
  );
}

updateClock();
setInterval(updateClock, 1000 * 3600);
