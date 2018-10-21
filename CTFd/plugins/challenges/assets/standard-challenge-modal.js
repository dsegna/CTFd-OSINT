window.challenge.data = undefined;

window.challenge.renderer = new markdownit({
    html: true,
});

window.challenge.preRender = function(){

};

window.challenge.render = function(markdown){
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function(){

};


window.challenge.submit = function(cb, preview){
    var chal_id = $('#chal-id').val();
    
    var nonce = $('#nonce').val();

	var x = $('#answer-input').attr('placeholder');;

	var y = $('#answer-url').val();
	var z = $('#answer-just').val();
	var delim = " | "

	var answer  = x+delim+y+delim+z+delim;
    var url = "/chal/";
    if (preview) {
        url = "/admin/chal/";
    }

    $.post(script_root + url + chal_id, {
        key: answer,
        nonce: nonce
    }, function (data) {
        cb(data);
    });
};