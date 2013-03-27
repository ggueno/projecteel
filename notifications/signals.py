from django.dispatch import Signal

notify = Signal(providing_args=[
    'recipient', 'actor', 'verb', 'level', 'action_object', 'target', 'description',
    'timestamp'
])
