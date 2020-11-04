Context Processors
==================

Django Site Utils provides context processors to allow including additional
variables for template rendering. The two context processors currently
available are::

  * ``'site_utils.context_processors.hostname'``: Exposes ``socket.gethostname()``
    to templates via the ``hostname`` variable.
  * ``'site_utils.context_processors.settings'``: Exposes ``django.conf.settings``
    to templates via the ``settings`` variable. Use with care, as the settings
    object contains passwords and other sensitive information.

To use these context processors in your project, add them to the list of
context proccessors in your ``TEMPLATES`` setting in your ``settings.py``::

    TEMPLATES = [
        {
            ...,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'site_utils.context_processors.hostname',
                    'site_utils.context_processors.settings',
                ],
            },
        },
    ]
