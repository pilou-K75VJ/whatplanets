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

function updateClock() {
  let now = new Date();
  seconds = (3600 * now.getHours() + 60 * now.getMinutes()
             + now.getSeconds() + now.getMilliseconds() / 1000)
            * Math.PI / 1800;
  drawClock(
    seconds * 2,
    seconds * 3,
    seconds * 5,
    seconds * 7,
    seconds * 11,
    seconds * 13,
    seconds * 17,
  );
}

setInterval(updateClock, 1000 / 10);
