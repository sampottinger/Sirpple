// jQuery initialization logic

var context;
var counter = 0;
var counts = new Array();
var images = new Array();
var postop = new Array();
var posleft = new Array();

$(document).ready(function() {
  img = new Image();

  //set up the accordion
	$( ".accordion" ).accordion({"autoHeight": false,
			"navigation": true});

  //set up drag and drop
  $(".draggable").draggable( { revert:'invalid', helper:'clone', appendTo: 'body' } )

  $(".droppable").droppable({
      drop: function(event, ui) {
        images[counter] = new Image();
        postop[counter] = ui.offset.top - $(this).offset().top;
       posleft[counter] = ui.offset.left - $(this).offset().left;
        images[counter].src = ui.draggable.attr('src');
        counts[counter] = 0;
        counter++;
      }})

  var canvas = document.getElementById('canvas');
  context = canvas.getContext('2d');
  context.fillStyle = "rgb(0,0,255)";
  context.fillRect(30,30,50,50);

  var rotate = setTimeout("doRotate()", 16);

});

function doRotate() {
  context.clearRect(0,0,500,650)
  for(i = 0; i < counter; i++)
  {
    context.save();
      context.translate(posleft[i],postop[i]);
      context.save();
        context.translate(20*Math.cos(counts[i]/20), 20*Math.sin(counts[i]/20));
        context.drawImage(images[i],0,0);
      context.restore();
    context.restore();
    counts[i]++;
  }
  setTimeout("doRotate()", 16);
}
