from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json
from django.db.models.loading import get_model
from core.models import EquipmentTag

MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)

# define the default models for tags and tagged items

def singularize(word):
    """Return the singular form of a word
 
    &gt;&gt;&gt; singularize('rabbits')
    'rabbit'
    &gt;&gt;&gt; singularize('potatoes')
    'potato'
    &gt;&gt;&gt; singularize('leaves')
    'leaf'
    &gt;&gt;&gt; singularize('knives')
    'knife'
    &gt;&gt;&gt; singularize('spies')
    'spy'
    """
    sing_rules = [lambda w: w[-3:] == 'ies' and w[:-3] + 'y',
                  lambda w: w[-4:] == 'ives' and w[:-4] + 'ife',
                  lambda w: w[-3:] == 'ves' and w[:-3] + 'f',
                  lambda w: w[-2:] == 'es' and w[:-2],
                  lambda w: w[-1:] == 's' and w[:-1],
                  lambda w: w,
                  ]
    word = word.strip()
    singleword = [f(word) for f in sing_rules if f(word) is not False][0]
    return singleword

def list_tags(request, tagName):
    """
    Returns a list of JSON objects with a `name` and a `value` property that
    all start like your query string `q` (not case sensitive).
    """
    query = request.GET.get('q', '')
    limit = request.GET.get('limit', MAX_SUGGESTIONS)
    if tagName != "tags":
        TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('core', singularize(tagName[0].upper()+tagName[1:])+"Tag"))
    else:
        TAG_MODEL = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODEL', ('taggit', "Tag"))
        
    TAG_MODEL = get_model(*TAG_MODEL)

    try:
        request.GET.get('limit', MAX_SUGGESTIONS)
        limit = min(int(limit), MAX_SUGGESTIONS)  # max or less
    except ValueError:
        limit = MAX_SUGGESTIONS

    tag_name_qs = TAG_MODEL.objects.filter(name__icontains=query).\
        values_list('name', flat=True)
    data = [{'name': n, 'value': n} for n in tag_name_qs[:limit]]

    return HttpResponse(json.dumps(data), mimetype='application/json')
