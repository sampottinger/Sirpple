steal( 'jquery/controller',
       'jquery/view/ejs',
	   'jquery/dom/form_params',
	   'jquery/controller/view',
	   'sirpple/models' )
	.then('./views/init.ejs', function($){

/**
 * @class Sirpple.GameObject.Create
 * @parent index
 * @inherits jQuery.Controller
 * Creates game_objects
 */
$.Controller('Sirpple.GameObject.Create',
/** @Prototype */
{
	init : function(){
		this.element.html(this.view());
	},
	submit : function(el, ev){
		ev.preventDefault();
		this.element.find('[type=submit]').val('Creating...')
		new Sirpple.Models.GameObject(el.formParams()).save(this.callback('saved'));
	},
	saved : function(){
		this.element.find('[type=submit]').val('Create');
		this.element[0].reset()
	}
})

});