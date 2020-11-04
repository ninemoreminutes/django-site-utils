Commands
========

Django Site Utils provides the following management commands for performing
site-wide administrative actions.

site_cleanup
------------

``site_cleanup`` runs a customizable list of cleanup functions that can help
to remove stale database content. Refer to ``SITE_CLEANUP_FUNCTIONS`` in
:doc:`settings` for the list of functions that will be run.

site_config
-----------

The ``site_config`` command updates the ``Sites`` model provided by the
``django.contrib.sites`` app. It can be used by deployment scripts to update
the database to reflect the domain(s) where project has been deployed, for
example::

    python manage.py site_config -n "Dev Site" -d "dev.example.com"

site_error_page
---------------

The ``site_error_page`` command generates error pages using the site's theme
and customizable templates. These error page files can be used by a frontend
web server (e.g. apache or nginx) to display errors outside of the Django
application while maintaining the look and feel of the Django site. For
example, the following command generates ``404.html`` and ``500.html`` files::

    python manage.py site_error_page --dest /path/to/webroot/ 404 500

For customization of the error messages and templates, refer to the
``SITE_ERROR_MESSAGES`` and ``SITE_ERROR_TEMPLATES`` settings under
:doc:`settings`.

site_notify
-----------

The ``site_notify`` command can be used to email users listed in the
``ADMINS`` or ``MANAGERS`` settings or any users in the database based on their
``is_staff`` or ``is_superuser`` status. The subject and body of the
notification are provided via the command line options, and the templates used
to render the message may be overridden for further customization.

For example, to notify ``ADMINS`` when a new version of the site is running::

    python manage.py site_notify --admins "Site Updated" "Site is now running commit abcdef on branch devel"

Or to notify all staff users of upcoming site maintenance::

    python manage.py site_notify --staff "Upcoming Maintenance" "The site will be down for maintenance on YYYY/MM/DD from 2:00-3:00 AM"

Refer to the ``SITE_NOTIFY_DEFAULT_RECIPIENTS``, ``SITE_NOTIFY_BODY_TEMPLATE``
and ``SITE_NOTIFY_SUBJECT_TEMPLATE`` settings in :doc:`settings` to further
customize notification defaults.

site_update
-----------

The ``site_update`` command runs multiple management commands together,
allowing for different named groups of commands. For example, running the
following command will run ``manage.py check``, ``manage.py migrate --fake-initial``
and ``manage.py collectstatic`` in order::

    python manage.py site_update

Refer to the ``SITE_UPDATE_COMMANDS`` setting in :doc:`settings` to
customize the default commands or define new groups of commands.
