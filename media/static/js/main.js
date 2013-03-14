// django jQuery namespace
var django = {
    "jQuery": jQuery
};

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

//Switch options on dropdown click
$('.dropdown-menu a.select').hide();
$('.dropdown-menu a').click(function(e){
    e.preventDefault();

    $('.dropdown-menu a').removeClass('select').show();
    $(this).addClass('select').hide();


    var toggle = $(this).parents('.dropdown-menu').prev();
    var value_current = $(toggle).data('value');
    var label_current = $(toggle).html();

    //console.log(toggle, value_current, label_current);

    $(toggle).attr('data-value',$(this).data('value'));
    $(toggle).html($(this).html());

    //$(this).attr('data-value',value_current);
    //$(this).html(label_current);

});

function follow_button(){
    $(".follow").click(function(){
        var follow_button = this;
        $.post($(this).attr('href'),function(data){
            if(data==true )
                if($(follow_button).hasClass('unactive')){
                    var link = $(follow_button).attr('href').replace('follow','unfollow');
                    $(follow_button).attr('href',link)
                    $(follow_button).removeClass('unactive');
                    $(follow_button).addClass('active');
                    $(follow_button).html("Suivi");

                }else{
                    var link = $(follow_button).attr('href').replace('unfollow','follow');
                    $(follow_button).attr('href',link)
                    $(follow_button).addClass('unactive');
                    $(follow_button).removeClass('active');
                    $(follow_button).html("Suivre");
                }
        });
        return false;
    });
}


function onoff_button(target, name, active, unactive){
    $(target).click(function(){
        var button = this;
        $.post($(this).attr('href'),function(data){
            if(data==true || data.state == true)
                if($(button).hasClass('unactive')){
                    var link = $(button).attr('href').replace(name,'un'+name);
                    $(button).attr('href',link);
                    $(button).removeClass('unactive');
                    $(button).addClass('active');
                    $(button).html(active);
                    //TODO : Add Unfollow hover
                }else{
                    var link = $(button).attr('href').replace('un'+name,name);
                    $(button).attr('href',link);
                    $(button).addClass('unactive');
                    $(button).removeClass('active');
                    $(button).html(unactive);
                }
        });
        return false;
    });
}

function initDatePicker(){
    /* French initialisation for the jQuery UI date picker plugin. */
    /* Written by Keith Wood (kbwood@virginbroadband.com.au) and Stéphane Nahmani (sholby@sholby.net). */
    jQuery(function($){
        $.datepicker.regional['fr'] = {clearText: 'Effacer', clearStatus: '',
            closeText: 'Fermer', closeStatus: 'Fermer sans modifier',
            prevText: '<Préc', prevStatus: 'Voir le mois précédent',
            nextText: 'Suiv>', nextStatus: 'Voir le mois suivant',
            currentText: 'Courant', currentStatus: 'Voir le mois courant',
            monthNames: ['Janvier','Février','Mars','Avril','Mai','Juin',
            'Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
            monthNamesShort: ['Jan','Fév','Mar','Avr','Mai','Jun',
            'Jul','Aoû','Sep','Oct','Nov','Déc'],
            monthStatus: 'Voir un autre mois', yearStatus: 'Voir un autre année',
            weekHeader: 'Sm', weekStatus: '',
            dayNames: ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'],
            dayNamesShort: ['Dim','Lun','Mar','Mer','Jeu','Ven','Sam'],
            dayNamesMin: ['Di','Lu','Ma','Me','Je','Ve','Sa'],
            dayStatus: 'Utiliser DD comme premier jour de la semaine', dateStatus: 'Choisir le DD, MM d',
            dateFormat: 'dd/mm/yy', firstDay: 0,
            firstDay : 1,
            initStatus: 'Choisir la date', isRTL: false};
        $.datepicker.setDefaults($.datepicker.regional['fr']);
    });

    $( ".datePicker" ).datepicker({ dateFormat: "dd/mm/yy" });
}

initDatePicker();
