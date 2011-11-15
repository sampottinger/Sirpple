steal('funcunit',function(){

module("Sirpple.GameObject.List", { 
	setup: function(){
		S.open("//sirpple/game_object/list/list.html");
	}
});

test("delete game_objects", function(){
	S('#create').click()
	
	// wait until grilled cheese has been added
	S('h3:contains(Grilled Cheese X)').exists();
	
	S.confirm(true);
	S('h3:last a').click();
	
	
	S('h3:contains(Grilled Cheese)').missing(function(){
		ok(true,"Grilled Cheese Removed")
	});
	
});


});