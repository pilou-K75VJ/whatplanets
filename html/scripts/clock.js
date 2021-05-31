let ctx = document.getElementById('clock').getContext('2d');

ctx.translate(125, 125);
ctx.rotate(-Math.PI / 2);

function drawClock(h, m, s, ms) {
  ctx.clearRect(-125, -125, 250, 250);

  let s_ = s + ms / 1000;
  let m_ = m + s_ / 60;
  let h_ = h + m_ / 60;

  let s_a = s_ * Math.PI / 30;
  let m_a = m_ * Math.PI / 30;
  let h_a = h_ * Math.PI / 6;

  ctx.fillStyle = 'rgba(1, 1, 1, 0.1)';
  ctx.beginPath();
  ctx.arc(0, 0, 110, 0, 2 * Math.PI);
  ctx.fill();

  ctx.lineCap = 'round';

  ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
  ctx.lineWidth = 10;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(50 * Math.cos(h_a), 50 * Math.sin(h_a));
  ctx.stroke();

  ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(80 * Math.cos(m_a), 80 * Math.sin(m_a));
  ctx.stroke();

  ctx.strokeStyle = 'rgba(0, 0, 0, 0.6)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(100 * Math.cos(s_a), 100 * Math.sin(s_a));
  ctx.stroke();

  ctx.fillStyle = 'rgba(0, 0, 0, 1)';
  ctx.beginPath();
  ctx.arc(0, 0, 10, 0, 2 * Math.PI);
  ctx.fill();
}

function updateClock() {
  let now = new Date();
  drawClock(
    now.getHours(),
    now.getMinutes(),
    now.getSeconds(),
    now.getMilliseconds()
  );
}

setInterval(updateClock, 1000 / 30);
