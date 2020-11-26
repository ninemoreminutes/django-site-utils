Patches
=======

Django Site Utils provides functions to monkey-patch certain Django internals. These functions are automatically
applied when included in ``SITE_PATCHES`` in :doc:`settings`.

``patch_runserver_addrport``
----------------------------

The ``site_utils.patches.patch_runserver_addrport`` function will use the ``RUNSERVER_DEFAULT_ADDR`` and
``RUNSERVER_DEFAULT_PORT`` settings to determine the default address and port used for
``manage.py runserver`` when not otherwise specified via command line options.

``patch_wsgi_handler_keep_alive``
---------------------------------

The ``site_utils.patches.patch_wsgi_handler_keep_alive`` function adds support for HTTP keep-alive connections to the
default WSGI handler.
