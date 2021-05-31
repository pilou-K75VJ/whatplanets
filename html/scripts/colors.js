let html = document.querySelector('html');
let body = document.querySelector('body');
let mushroom = document.querySelector('#mushroom');

class bgColors {
  static lightRed = '#FFBFDF';
  static darkRed = '#802050';
  static lightGreen = '#DFFFBF';
  static darkGreen = '#508020';
  static lightBlue = '#BFDFFF';
  static darkBlue = '#205080';
}

function rgbToHex(rgbString) {
  let rgb = /rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)/.exec(rgbString);
  let r = parseInt(rgb[1]);
  let g = parseInt(rgb[2]);
  let b = parseInt(rgb[3]);
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

mushroom.onclick = function() {
  switch (rgbToHex(html.style.backgroundColor)) {
    case bgColors.darkBlue:
      html.style.backgroundColor = bgColors.darkGreen;
      body.style.backgroundColor = bgColors.lightGreen;
      break;
    case bgColors.darkGreen:
      html.style.backgroundColor = bgColors.darkRed;
      body.style.backgroundColor = bgColors.lightRed;
      break;
    default:
      html.style.backgroundColor = bgColors.darkBlue;
      body.style.backgroundColor = bgColors.lightBlue;
  }
}

html.style.backgroundColor = bgColors.darkBlue;
body.style.backgroundColor = bgColors.lightBlue;
