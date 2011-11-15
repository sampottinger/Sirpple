steal( 'jquery/controller',
	   'jquery/view/ejs',
	   'jquery/controller/view',
	   'sirpple/models')
.then( './views/init.ejs', 
       './views/project.ejs', 
       function($){

/**
 * @class Sirpple.Project.List
 * @parent index
 * @inherits jQuery.Controller
 * Lists projects and lets you destroy them.
 */
$.Controller('Sirpple.Project.List',
/** @Static */
{
	defaults : {}
},
/** @Prototype */
{
	init : function(){
		this.element.html(this.view('init',Sirpple.Models.Project.findAll()) );
	},
	'.destroy click': function( el ){
		if(confirm("Are you sure you want to destroy?")){
			el.closest('.project').model().destroy();
		}
	},
	"{Sirpple.Models.Project} destroyed" : function(Project, ev, project) {
		project.elements(this.element).remove();
	},
	"{Sirpple.Models.Project} created" : function(Project, ev, project){
		this.element.append(this.view('init', [project]))
	},
	"{Sirpple.Models.Project} updated" : function(Project, ev, project){
		project.elements(this.element)
		      .html(this.view('project', project) );
	}
});

});