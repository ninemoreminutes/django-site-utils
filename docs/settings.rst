Settings
========

.. SITE_CLEANUP_FUNCTIONS
   ----------------------

   This setting is a list or tuple of functions that are execute when for the
   ``site_cleanup`` command.

   Its default value is::

      SITE_CLEANUP_FUNCTIONS = [
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
message.  It can be overridden by the --body-template option to the
``site_notify`` command.

Its default value is::

   SITE_NOTIFY_BODY_TEMPLATE = 'site_utils/site_notify_body.txt'

SITE_NOTIFY_SUBJECT_TEMPLATE
----------------------------

This setting specifies a template for rendering the subject of a site
notification  message.  It can be overridden by the --subject-template option
to the ``site_notify`` command.

Its default value is::

   SITE_NOTIFY_SUBJECT_TEMPLATE = 'site_utils/site_notify_subject.txt'

SITE_UPDATE_COMMANDS
--------------------

The default value if not specified is::

   SITE_UPDATE_COMMANDS = {
      'default': [
         'syncdb',
         {'command': 'migrate', 'ifapp': 'south'},
         {'command': 'collectstatic', 'ifapp': 'staticfiles'},
      ]
   }

