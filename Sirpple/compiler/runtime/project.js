//set main namespace
//TODO: set this dynamically
/goog.provide('project');


//get requirements
//TODO: set these up dynamically
goog.require('lime.Director');
goog.require('lime.Scene');
goog.require('lime.Layer');
goog.require('lime.Circle');
goog.require('lime.Label');
goog.require('lime.animation.Spawn');
goog.require('lime.animation.FadeTo');
goog.require('lime.animation.ScaleTo');
goog.require('lime.animation.MoveTo');

{{worlds}}

{{game_objects}}

// entrypoint
project.start = function(){

    var director = new lime.Director(document.body,1024,768),
    var scene = new {{starting_world}}()

    // set current scene active
    director.replaceScene(scene);

}


//this is required for outside access after code is compiled in ADVANCED_COMPILATIONS mode
goog.exportSymbol('project.start', project.start);
