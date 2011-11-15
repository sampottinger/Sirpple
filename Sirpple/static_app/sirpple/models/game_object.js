steal('jquery/model', function(){

/**
 * @class Sirpple.Models.GameObject
 * @parent index
 * @inherits jQuery.Model
 * Wraps backend game_object services.  
 */
$.Model('Sirpple.Models.GameObject',
/* @Static */
{
	findAll: "/game_objects.json",
  	findOne : "/game_objects/{id}.json", 
  	create : "/game_objects.json",
 	update : "/game_objects/{id}.json",
  	destroy : "/game_objects/{id}.json"
},
/* @Prototype */
{});

})