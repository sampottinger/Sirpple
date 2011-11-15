//js sirpple/scripts/doc.js

load('steal/rhino/rhino.js');
steal("documentjs").then(function(){
	DocumentJS('sirpple/sirpple.html', {
		markdown : ['sirpple']
	});
});