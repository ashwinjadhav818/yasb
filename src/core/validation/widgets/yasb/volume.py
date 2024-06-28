
DEFAULTS = {
    'label': "{volume_icon}",
    'label_alt': "{volume_icon} {volume_level}%",
    'update_interval': 1000,
    'callbacks': {
        'on_left': 'toggle_label',
        'on_middle': 'do_nothing',
        'on_right': 'do_nothing'
    },
    'volume_icons': [
        "\ueee8",  # Icon for muted
        "\uf026",  # Icon for 0% volume
        "\uf027",  # Icon for 1-25% volume
        "\uf027",  # Icon for 26-50% volume
        "\uf028",  # Icon for 51-75% volume
        "\uf028"   # Icon for 76-100% volume
    ]
}


VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'default': DEFAULTS['label']
    },
    'label_alt': {
        'type': 'string',
        'default': DEFAULTS['label_alt']
    },
    'update_interval': {
        'type': 'integer',
        'default': DEFAULTS['update_interval'],
        'min': 0,
        'max': 60000
    },
    'volume_icons': {
        'type': 'list',
        'default': DEFAULTS['volume_icons'],
        "schema": {
            'type': 'string',
            'required': False
        }
    },
    'callbacks': {
        'type': 'dict',
        'schema': {
            'on_left': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_left'],
            },
            'on_middle': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_middle'],
            },
            'on_right': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_right'],
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
