DEFAULTS = {
    'label': "{volume_icon} {volume_level}%",
    'label_alt': "{volume_icon} {volume_level}%",
    'update_interval': 1000,
    'volume_icons': [
        "\udb81\udf5f",
        "\udb81\udf5f",
        "\udb81\udd7f",
        "\udb81\udd80",
        "\udb81\udd7e"
    ],
    'callbacks': {
        'on_left': 'do_nothing',
        'on_middle': 'do_nothing',
        'on_right': 'do_nothing'
    },
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
    'volume_icons': {
        'type': 'list',
        'default': DEFAULTS['volume_icons'],
        "schema": {
            'type': 'string',
            'required': False
        }
    },
    'update_interval': {
        'type': 'integer',
        'default': 1000,
        'min': 0,
        'max': 60000
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
