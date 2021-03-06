Introduction
============

To get started using Django-Site-Utils, follow the instructions below to
install it and add it to your Django project.

Installation
------------

Install the ``django-site-utils`` package using `pip <http://www.pip-installer.org/>`_::

   pip install django-site-utils

Using a `virtual environment <http://www.virtualenv.org/>`_ is highly
recommended instead of installing into your system wide site-packages
directory.

Configuration
-------------

Add ``site_utils`` to your project's INSTALLED_APPS::

    INSTALLED_APPS = (
       ...
       'site_utils',
       ...
    )

Usage
-----

Django-Site-Utils is typically used by invoking one of its management commands::

    ./manage.py *<command>*

Where *<command>* is one of the following:

* ``site_cleanup``
* ``site_config``
* ``site_error_page``
* ``site_notify``
* ``site_update``

Any command can be followed with the ``--help`` option to view the available
command line arguments.

Next Steps
----------

To learn more about a specific command, read its detailed documentation under
:doc:`commands` or configure it with custom :doc:`settings`. Refer to :doc:`views`
to learn more about the included error handlers and views and :doc:`context_processors`
to learn about the available context processors.
