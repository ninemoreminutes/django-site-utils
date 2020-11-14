Settings
========

SITE_CLEANUP_FUNCTIONS
----------------------

This setting is a list or tuple of functions that are executed for the
``site_cleanup`` command.

Its default value is::

    SITE_CLEANUP_FUNCTIONS = [
        'site_utils.cleanup.cleanup_stale_content_types',
        'site_utils.cleanup.cleanup_unused_database_tables',
    ]

SITE_NOTIFY_DEFAULT_RECIPIENTS
------------------------------

This setting specifies the default recipients for a site notification when none
are explicitly given via command line arguments.

The default value for this setting is::

    SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins',)

SITE_NOTIFY_BODY_TEMPLATE
----------------------------

This setting specifies a template for rendering the body of a site notification
message.  It can be overridden by the ``--body-template`` option to the
``site_notify`` command.

Its default value is::

    SITE_NOTIFY_BODY_TEMPLATE = 'site_utils/site_notify_body.txt'

SITE_NOTIFY_SUBJECT_TEMPLATE
----------------------------

This setting specifies a template for rendering the subject of a site
notification  message.  It can be overridden by the ``--subject-template`` option
to the ``site_notify`` command.

Its default value is::

    SITE_NOTIFY_SUBJECT_TEMPLATE = 'site_utils/site_notify_subject.txt'

SITE_UPDATE_COMMANDS
--------------------

Each dictionary key in ``SITE_UPDATE_COMMANDS`` defines the name for a group
of commands that can be run together. The ``"default"`` named group will be
used when the ``site_update`` command is invoked without any additional
arguments.

Each dictionary value is a list of management commands to be run in order. If
a command is provided as a string, it is run unconditionally with its default
options. If a command is provided instead as a tuple::

  * The first item is the command name.
  * The second item is a list or tuple of positional arguments.
  * The third item is a dictionary of keyword arguments, which represent any
    command line flags that would be passed to the command. In most cases, a
    flag such as ``--optional-parameter`` would be represented as
    ``optional_parameter`` when used as a keyword argument.
  * The fourth item specifies an app that must be installed in order for the
    command to run. Otherwise, the command is skipped.

The default value for this setting is::

    SITE_UPDATE_COMMANDS = {
        'default': [
            'check',
            ('migrate, (), {'fake_initial': True}),
            ('collectstatic', (), {}, 'staticfiles'),
        ],
    }

SITE_ERROR_MESSAGES
-------------------

The ``SITE_ERROR_MESSAGES`` setting defines default error messages to use when
rendering the built-in error handler views or when generating static error
pages.

The key for each item is the HTTP response status code, and the value is a
two-tuple defining the title and body displayed on the error page. Additional
status codes defined in your own settings will be merged with the default
messages.

The default error messages defined are::

    SITE_ERROR_MESSAGES = {
        400: (
            _('Bad Request'),
            _('The request could not be understood by the server.'),
        ),
        403: (
            _('Forbidden'),
            _('You do not have permission to access the requested resource.'),
        ),
        404: (
            _('Not Found'),
            _('The requested page could not be found.'),
        ),
        500: (
            _('Server Error'),
            _('An internal server error has occurred.'),
        ),
        502: (
            _('Bad Gateway'),
            _('An invalid response was received from the upstream server.'),
        ),
        503: (
            _('Server Unavailable'),
            _('The server is currently unavailable.'),
        ),
        504: (
            _('Gateway Timeout'),
            _('Did not receive a timely response from the upstream server.'),
        ),
    }

SITE_ERROR_TEMPLATES
--------------------

The ``SITE_ERROR_TEMPLATES`` setting is a list of two-tuples to allow
customization of the templates used to render error pages, enabling different
templates to be used for different sections of the site.

The first item in the two-tuple is a regular expression that will be matched
against the request path (the regular expression should not include a leading
forward slash ``'/'``). If the expression matches, the second item in the
two-tuple refers to the template path to be used to render the error page.

If no regular expressions match, the default template ``'site_utils/error.html'``
will be used.

The default value is::

    SITE_ERROR_TEMPLATES = [
        (r'', 'site_utils/error.html'),
    ]

SITE_PATCHES
------------

This setting is a list or tuple of functions that are executed once the Django models
have been populated (via the ``AppConfig.ready()`` method). These functions can be used
to monkeypatch other libraries or perform other project initialization.

Its default value is::

    SITE_PATCHES = [
        'site_utils.patches.patch_runserver_addrport',
    ]

The included patch function above will use the ``RUNSERVER_DEFAULT_ADDR`` and
``RUNSERVER_DEFAULT_PORT`` settings to determine the default address and port used for
``manage.py runserver`` when not otherwise specified via command line options.
