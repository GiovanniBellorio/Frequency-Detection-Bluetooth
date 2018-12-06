window.onpageshow = function(event) {
    if (event.persisted) {
        window.location.reload() 
    }
};

$('.js-pscroll').each(function(){
	var ps = new PerfectScrollbar(this);
	$(window).on('resize', function(){
		ps.update();
	})
});