DEFAULTS = {
    'label_offline': 'Komorebi Offline',
    'label_workspace_btn': '{index}',
    'label_default_name': '',
    'label_zero_index': False,
    'hide_empty_workspaces': False,
    'preview_workspace': False,
    'callbacks': {
        'on_left': 'activate',
        'on_middle': 'rename_temporary',
        'on_right': 'rename_permanent'
    }

}

ALLOWED_CALLBACKS = [
    'activate',
    'rename_temporary',
    'rename_permanent',
    'do_nothing'
]

VALIDATION_SCHEMA = {
    'label_offline': {
        'type': 'string',
        'default': DEFAULTS['label_offline']
    },
    'label_workspace_btn': {
        'type': 'string',
        'default': DEFAULTS['label_workspace_btn']
    },
    'label_default_name': {
        'type': 'string',
        'default': DEFAULTS['label_default_name']
    },
    'label_zero_index': {
        'type': 'boolean',
        'default': DEFAULTS['label_zero_index']
    },
    'hide_empty_workspaces': {
        'type': 'boolean',
        'default': DEFAULTS['hide_empty_workspaces']
    },
    'preview_workspace': {
        'type': 'boolean',
        'default': DEFAULTS['preview_workspace']
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
                'default': DEFAULTS['callbacks']['on_middle'],
                'allowed': ALLOWED_CALLBACKS
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
