Views
=====

Django Site Utils offers additional views for error handling, eliminating the
need to define your own within your projects.

Handlers
--------

``site_utils.handlers`` defines the
`default error handler views <https://docs.djangoproject.com/en/3.1/topics/http/views/#customizing-error-views>`_
needed by any Django project. To use, import the handlers into your project's main ``urls.py``::

    from site_utils.handlers import handler400, handler403, handler404, handler500  # noqa

Debug Views
-----------

When running with ``DEBUG = True``, Django does not normally render error pages.
In order to preview error pages during development, you can include ``site_utils.urls``
in your ``urls.py`` alongside your existing URL patterns::

    from django.conf import settings
    from django.urls import include, re_path
    import site_utils.urls
    
    urlpatterns = [...]
    
    if settings.DEBUG:
        urlpatterns += [
            re_path(r'', include(site_utils.urls)),
        ]

Now, visiting ``http://<your-dev-server>/<status-code>.html``, where status
code is one of ``400``, ``403``, ``404``, ``500``, will render an example error
page.

Error Views
-----------

Each of the error handlers above uses the views defined in ``site_utils.views``
(``handle_400``, ``handle_403``, ``handle_404`` and ``handle_500``),
which all rely on the ``handle_error`` view. This common view may be called by
your own view functions to define error handlers for other HTTP response status
codes.

Customization
-------------

To customize the messages displayed on each error page or change the templates
used to render each error page, refer to the ``SITE_ERROR_MESSAGES`` and
``SITE_ERROR_TEMPLATES`` :doc:`settings`.
