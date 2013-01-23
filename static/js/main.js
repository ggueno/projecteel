// django jQuery namespace
var django = {
    "jQuery": jQuery.noConflict(true)
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