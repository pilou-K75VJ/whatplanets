(function() {

const html = document.querySelector('html');
const body = document.querySelector('body');
const earthLogo = document.querySelector('#earth-logo');

const colors = {
  'lightRed': '#FFBFDF',
  'darkRed': '#802050',
  'lightGreen': '#DFFFBF',
  'darkGreen': '#508020',
  'lightBlue': '#BFDFFF',
  'darkBlue': '#205080'
};

function rgbToHex(rgbString) {
  let rgb = /rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)/.exec(rgbString);
  return "#" + ((1 << 24)
                + (parseInt(rgb[1]) << 16)
                + (parseInt(rgb[2]) << 8)
                + parseInt(rgb[3])).toString(16).slice(1);
}

earthLogo.onclick = function() {
  switch (rgbToHex(html.style.backgroundColor)) {
    case colors.darkBlue:
      html.style.backgroundColor = colors.darkGreen;
      body.style.backgroundColor = colors.lightGreen;
      break;
    case colors.darkGreen:
      html.style.backgroundColor = colors.darkRed;
      body.style.backgroundColor = colors.lightRed;
      break;
    default:
      html.style.backgroundColor = colors.darkBlue;
      body.style.backgroundColor = colors.lightBlue;
  }
};

html.style.backgroundColor = colors.darkBlue;
body.style.backgroundColor = colors.lightBlue;

})();
