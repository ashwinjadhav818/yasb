DEFAULTS = {
    'label': "{win[title]}",
    'label_alt': "[class_name='{win[class_name]}' exe='{win[process][name]}' hwnd={win[hwnd]}]",
    'max_length': None,
    'max_length_ellipsis': '...',
    'ignore_windows': {
        'classes': [],
        'processes': [],
        'titles': []
    },
    'callbacks': {
        'on_left': 'activate_window',
        'on_middle': 'toggle_label',
        'on_right': 'remove_window'
    }
}

ALLOWED_CALLBACKS = [
    "activate_window",
    "remove_window",
    "toggle_label",
    "do_nothing"
]


VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'default': DEFAULTS['label']
    },
    'label_alt': {
        'type': 'string',
        'default': DEFAULTS['label_alt']
    },
    'max_length': {
        'type': 'integer',
        'min': 1,
        'nullable': True,
        'default': DEFAULTS['max_length']
    },
    'max_length_ellipsis': {
        'type': 'string',
        'default': DEFAULTS['max_length_ellipsis']
    },
    'ignore_window': {
        'type': 'dict',
        'schema': {
            'classes': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                },
                'default': DEFAULTS['ignore_windows']['classes']
            },
            'processes': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                },
                'default': DEFAULTS['ignore_windows']['processes']
            },
            'titles': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                },
                'default': DEFAULTS['ignore_windows']['titles']
            }
        },
        'default': DEFAULTS['ignore_windows']
    },
    'callbacks': {
        'type': 'dict',
        'schema': {
            'on_left': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_left'],
                'allowed': ALLOWED_CALLBACKS
            },
            'on_middle': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_middle'],
                'allowed': ALLOWED_CALLBACKS
            },
            'on_right': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_right'],
                'allowed': ALLOWED_CALLBACKS
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
