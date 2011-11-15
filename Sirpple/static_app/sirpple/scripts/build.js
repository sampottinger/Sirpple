//steal/js sirpple/scripts/compress.js

load("steal/rhino/rhino.js");
steal('steal/build').then('steal/build/scripts','steal/build/styles',function(){
	steal.build('sirpple/scripts/build.html',{to: 'sirpple'});
});
