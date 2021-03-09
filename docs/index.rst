.. Django-Site-Utils documentation master file.

Django-Site-Utils
=================

The Django-Site-Utils library provides a reusable Django application with management commands for site-wide
administrative actions, along with functions for common tasks often needed by any Django site.

Management commands include:
 * ``site_cleanup`` : Cleanup stale data and tables.
 * ``site_config`` : Update the Site name and domain.
 * ``site_error_pages`` : Generate static error pages based on your site's theme.
 * ``site_notify`` : Send notifications to administrators and staff.
 * ``site_update`` : Run groups of management commands at once.

Other features include:
 * Error views and handlers.
 * Template context processors.
 * Admin mixin classes.
 * Functions to patch Django internals.

It is tested against:
 * Django 1.11 (Python 3.5 and 3.6)
 * Django 2.0 (Python 3.5, 3.6 and 3.7)
 * Django 2.1 (Python 3.5, 3.6 and 3.7)
 * Django 2.2 (Python 3.5, 3.6, 3.7, 3.8 and 3.9)
 * Django 3.0 (Python 3.6, 3.7, 3.8 and 3.9)
 * Django 3.1 (Python 3.6, 3.7, 3.8 and 3.9)
 * Django 3.2 pre-release (Python 3.6, 3.7, 3.8 and 3.9)
 * Django main/4.0 (Python 3.8 and 3.9)

.. toctree::
   :maxdepth: 2

   intro
   commands
   settings
   views
   context_processors
   admin
   patches

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`

.. * :ref:`search`
