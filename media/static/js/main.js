// django jQuery namespace
var django = {
    "jQuery": jQuery
};

django.jQuery(function() {

	var options = {
		inputs: {
		    'username': {
		      filters: 'required username exclude',
		      data: { exclude: ['user', 'username', 'admin'] }
		    },
		    'date': { filters: 'date' },
		    'comments': {
		      filters: 'min max',
		      data: { min: 50, max: 200 }
		    },
		    'colors': {
		      filters: 'exclude',
		      data: { exclude: ['default'] },
		      errors: { exclude: 'Choisissez une couleur de la liste' }
		    },
		    'langs[]': {
		      filters: 'min',
		      data: { min: 2 },
		      errors: { min: 'Check at least <strong>2</strong> languages.' }
		    },
		    'options': {
		      filters: 'min',
		      data: { min: 1 },
		      errors: { min: 'Check only <strong>1</strong> option.' }
		    }
		},
		responsiveAt: 100
	}
	var $myform = django.jQuery('#my-form, .PTform').idealforms(options).data('idealforms');

});

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});


$(".comment_form").submit(function(e){
		$.post($(this).attr('action'),$(this).serialize()).done(function(data){

        });
        return false;
    });


$(".delete-comment").click(function(e){
	var parent = $(this).parent();
	$.post($(this).attr('href'),function(data){
		$(parent).fadeOut();
	});
	return false;
});

//Generic tabbed nav fonction
$('ul.tabs').each(function(){
    // For each set of tabs, we want to keep track of
    // which tab is active and it's associated content
    var $active, $content, $links = $(this).find('a');

    // If the location.hash matches one of the links, use that as the active tab.
    // If no match is found, use the first link as the initial active tab.
    $active = $($links.filter('[href="'+location.hash+'"]')[0] || $links[0]);
    $active.addClass('active');
    $content = $($active.attr('href'));

    // Hide the remaining content
    $links.not($active).each(function () {
        $($(this).attr('href')).hide();
    });

    // Bind the click event handler
    $(this).on('click', 'a', function(e){
        // Make the old tab inactive.
        $active.removeClass('active');
        $content.hide();

        // Update the variables with the new link and content
        $active = $(this);
        $content = $($(this).attr('href'));

        // Make the tab active.
        $active.addClass('active');
        $content.show();

        // Prevent the anchor's default click action
        e.preventDefault();
    });
});