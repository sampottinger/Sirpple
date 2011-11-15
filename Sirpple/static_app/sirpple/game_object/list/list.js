steal( 'jquery/controller',
	   'jquery/view/ejs',
	   'jquery/controller/view',
	   'sirpple/models' )
.then( './views/init.ejs', 
       './views/game_object.ejs', 
       function($){

/**
 * @class Sirpple.GameObject.List
 * @parent index
 * @inherits jQuery.Controller
 * Lists game_objects and lets you destroy them.
 */
$.Controller('Sirpple.GameObject.List',
/** @Static */
{
	defaults : {}
},
/** @Prototype */
{
	init : function(){
		this.element.html(this.view('init',Sirpple.Models.GameObject.findAll()) )
	},
	'.destroy click': function( el ){
		if(confirm("Are you sure you want to destroy?")){
			el.closest('.game_object').model().destroy();
		}
	},
	"{Sirpple.Models.GameObject} destroyed" : function(GameObject, ev, game_object) {
		game_object.elements(this.element).remove();
	},
	"{Sirpple.Models.GameObject} created" : function(GameObject, ev, game_object){
		this.element.append(this.view('init', [game_object]))
	},
	"{Sirpple.Models.GameObject} updated" : function(GameObject, ev, game_object){
		game_object.elements(this.element)
		      .html(this.view('game_object', game_object) );
	}
});

});