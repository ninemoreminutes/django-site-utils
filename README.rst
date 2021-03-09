|Build Status| |PyPI Version| |PyPI License| |Python Versions| |Django Versions| |Read the Docs|

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

Documentation can be found at `Read The Docs <http://django-site-utils.readthedocs.io/>`_.

It is tested against:
 * Django 1.11 (Python 3.5 and 3.6)
 * Django 2.0 (Python 3.5, 3.6 and 3.7)
 * Django 2.1 (Python 3.5, 3.6 and 3.7)
 * Django 2.2 (Python 3.5, 3.6, 3.7, 3.8 and 3.9)
 * Django 3.0 (Python 3.6, 3.7, 3.8 and 3.9)
 * Django 3.1 (Python 3.6, 3.7, 3.8 and 3.9)
 * Django 3.2 pre-release (Python 3.6, 3.7, 3.8 and 3.9)
 * Django main/4.0 (Python 3.8 and 3.9)

.. |Build Status| image:: https://img.shields.io/github/workflow/status/ninemoreminutes/django-site-utils/test
   :target: https://github.com/ninemoreminutes/django-site-utils/actions?query=workflow%3Atest
.. |PyPI Version| image:: https://img.shields.io/pypi/v/django-site-utils.svg
   :target: https://pypi.python.org/pypi/django-site-utils/
.. |PyPI License| image:: https://img.shields.io/pypi/l/django-site-utils.svg
   :target: https://pypi.python.org/pypi/django-site-utils/
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/django-site-utils.svg
   :target: https://pypi.python.org/pypi/django-site-utils/
.. |Django Versions| image:: https://img.shields.io/pypi/djversions/django-site-utils.svg
   :target: https://pypi.org/project/django-site-utils/
.. |Read the Docs| image:: https://img.shields.io/readthedocs/django-site-utils.svg
   :target: http://django-site-utils.readthedocs.io/
