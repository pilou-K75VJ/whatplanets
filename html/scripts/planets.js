class plColors {
  static sun = '#ffd400';
  static mer = '#7f7f7f';
  static ven = '#afafaf';
  static lun = '#f7f7f7';
  static mar = '#893400';
  static jup = '#89632a';
  static sat = '#56451a';
}

let ctx = document.getElementById('planets').getContext('2d');
ctx.translate(125, 125);

function drawHand(color, angle, size = 100,
                  width = 5, alpha = 0.8) {
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(size * Math.cos(angle), size * Math.sin(angle));
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
  // Get raw CSV
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
  let nextIndex = 0;
  for (let i = 1; i < nRows - 1; i++) {
    let [yyyy, mm, dd] = rows[i].slice(0, 10).split('-');
    if (new Date(Date.UTC(yyyy, mm, dd)) > date) {
      nextIndex = i;
      test.textContent += mm + ' ';
      test.textContent += new Date(Date.UTC(yyyy, parseInt(mm), dd));
;
      break;
    }
  }
  let [date1, lon1, lat1] = rows[nextIndex - 1].split(',');
  let [y1, m1, d1] = date1.split('-');

  let [date2, lon2, lat2] = rows[nextIndex].split(',');
  let [y2, m2, d2] = date2.split('-');

  test.textContent += ' ';
  return -(parseFloat(lon1));
}

function drawClock(sun, mer, ven,
                   lun, mar, jup, sat) {
  ctx.clearRect(-125, -125, 250, 250);
  drawDisk('black', 110, alpha=0.6);

  ctx.lineCap = 'round';
  drawHand(plColors.sun, sun);
  drawHand(plColors.mer, mer);
  drawHand(plColors.ven, ven);
  drawHand(plColors.lun, lun);
  drawHand(plColors.mar, mar);
  drawHand(plColors.jup, jup);
  drawHand(plColors.sat, sat);

  drawDisk('white', 10);
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
