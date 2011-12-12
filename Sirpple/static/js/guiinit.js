// jQuery initialization logic

var context;
var count = 0;

$(document).ready(function() {

  //set up the accordion
	$( ".accordion" ).accordion({"autoHeight": false,
			"navigation": true});

  var canvas = document.getElementById('canvas');
  context = canvas.getContext('2d');
  context.fillStyle = "rgb(0,0,255)";
  context.fillRect(30,30,50,50);

  var rotate = setTimeout("doRotate()", 16);

});

function doRotate() {
  context.clearRect(0,0,500,650)
  context.save();
    context.translate(250,250);
    context.save();
      context.rotate(count / 10);
      context.fillRect(-10,-10,10,10);
    context.restore();
  context.restore();
  setTimeout("doRotate()", 16);
  count++;
}
