// jQuery initialization logic

var context;
var count = 0;
var img;
var postop;
var posleft;

$(document).ready(function() {
  img = new Image();

  //set up the accordion
	$( ".accordion" ).accordion({"autoHeight": false,
			"navigation": true});

  //set up drag and drop
  $(".draggable").draggable( { revert:'invalid', helper:'clone', appendTo: 'body' } )

  $(".droppable").droppable({
      drop: function(event, ui) {
        img = new Image();
        postop = ui.offset.top - $(this).offset().top;
        posleft = ui.offset.left - $(this).offset().left;
        img.src = ui.draggable.attr('src');
      }})

  var canvas = document.getElementById('canvas');
  context = canvas.getContext('2d');
  context.fillStyle = "rgb(0,0,255)";
  context.fillRect(30,30,50,50);

  var rotate = setTimeout("doRotate()", 16);

});

function doRotate() {
  context.clearRect(0,0,500,650)
  context.save();
    context.translate(posleft,postop);
    context.save();
      context.translate(20*Math.cos(count/20), 20*Math.sin(count/20));
      context.drawImage(img,0,0);
    context.restore();
  context.restore();
  setTimeout("doRotate()", 16);
  count++;
}
