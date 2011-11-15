steal("funcunit/qunit", "sirpple/fixtures", "sirpple/models/game_object.js", function(){
	module("Model: Sirpple.Models.GameObject")
	
	test("findAll", function(){
		expect(4);
		stop();
		Sirpple.Models.GameObject.findAll({}, function(game_objects){
			ok(game_objects)
	        ok(game_objects.length)
	        ok(game_objects[0].name)
	        ok(game_objects[0].description)
			start();
		});
		
	})
	
	test("create", function(){
		expect(3)
		stop();
		new Sirpple.Models.GameObject({name: "dry cleaning", description: "take to street corner"}).save(function(game_object){
			ok(game_object);
	        ok(game_object.id);
	        equals(game_object.name,"dry cleaning")
	        game_object.destroy()
			start();
		})
	})
	test("update" , function(){
		expect(2);
		stop();
		new Sirpple.Models.GameObject({name: "cook dinner", description: "chicken"}).
	            save(function(game_object){
	            	equals(game_object.description,"chicken");
	        		game_object.update({description: "steak"},function(game_object){
	        			equals(game_object.description,"steak");
	        			game_object.destroy();
						start();
	        		})
	            })
	
	});
	test("destroy", function(){
		expect(1);
		stop();
		new Sirpple.Models.GameObject({name: "mow grass", description: "use riding mower"}).
	            destroy(function(game_object){
	            	ok( true ,"Destroy called" )
					start();
	            })
	})
})