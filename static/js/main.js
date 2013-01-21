// django jQuery namespace
var django = {
    "jQuery": jQuery.noConflict(true)
};
$ = django.jQuery;
var options = {
	inputs: {
	  // The name attribute of the input in quotes
	  'PTinput': {
	    filters: 'required min',
	    data: { min: 10 },
	    errors: { min: 'At least 10 characters' },
	    flags: 'noclass noinvalidicon'
	  }
	}
}
var $myform = $('#my-form').idealforms(options).data('idealforms');