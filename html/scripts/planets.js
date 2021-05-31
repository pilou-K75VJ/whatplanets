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

function drawClock(sun, mer, ven,
                   lun, mar, jup, sat) {
  ctx.clearRect(-125, -125, 250, 250);

  ctx.globalAlpha = 0.6;
  ctx.fillStyle = 'black';
  ctx.beginPath();
  ctx.arc(0, 0, 110, 0, 2 * Math.PI);
  ctx.fill();

  ctx.lineCap = 'round';
  ctx.globalAlpha = 0.8;

  ctx.strokeStyle = plColors.sun;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(sun), 100 * Math.sin(sun));
  ctx.stroke();

  ctx.strokeStyle = plColors.mer;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(mer), 100 * Math.sin(mer));
  ctx.stroke();

  ctx.strokeStyle = plColors.ven;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(ven), 100 * Math.sin(ven));
  ctx.stroke();

  ctx.strokeStyle = plColors.lun;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(lun), 100 * Math.sin(lun));
  ctx.stroke();

  ctx.strokeStyle = plColors.mar;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(mar), 100 * Math.sin(mar));
  ctx.stroke();

  ctx.strokeStyle = plColors.jup;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(jup), 100 * Math.sin(jup));
  ctx.stroke();

  ctx.strokeStyle = plColors.sat;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(sat), 100 * Math.sin(sat));
  ctx.stroke();

  ctx.globalAlpha = 1;
  ctx.fillStyle = 'white';
  ctx.beginPath();
  ctx.arc(0, 0, 10, 0, 2 * Math.PI);
  ctx.fill();

}

function updateClock() {
  let now = new Date();
  seconds = (3600 * now.getHours() + 60 * now.getMinutes()
             + now.getSeconds() + now.getMilliseconds() / 1000)
            * Math.PI / 30;
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

setInterval(updateClock, 1000 / 30);
