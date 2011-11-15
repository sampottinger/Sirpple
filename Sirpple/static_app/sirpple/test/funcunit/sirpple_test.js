steal("funcunit", function(){
	module("sirpple test", { 
		setup: function(){
			S.open("//sirpple/sirpple.html");
		}
	});
	
	test("Copy Test", function(){
		equals(S("h1").text(), "Welcome to JavaScriptMVC 3.2!","welcome text");
	});
})