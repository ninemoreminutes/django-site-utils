# Python
import threading

_runserver_addrport_patched = threading.Event()
_wsgi_handler_keep_alive_patched = threading.Event()


def patch_runserver_addrport():
    if _runserver_addrport_patched.is_set():
        return
    _runserver_addrport_patched.set()

    # Use the addr/port defined in settings for runserver if not specified on the command line.
    from django.conf import settings
    default_addr = getattr(settings, 'RUNSERVER_DEFAULT_ADDR', '127.0.0.1')
    default_port = getattr(settings, 'RUNSERVER_DEFAULT_PORT', 8000)

    from django.core.management.commands import runserver as core_runserver
    original_handle = core_runserver.Command.handle

    def handle(self, *args, **options):
        if not options.get('addrport'):
            options['addrport'] = '%s:%d' % (default_addr, int(default_port))
        elif options.get('addrport').isdigit():
            options['addrport'] = '%s:%d' % (default_addr, int(options['addrport']))
        return original_handle(self, *args, **options)

    core_runserver.Command.handle = handle


def patch_wsgi_handler_keep_alive():
    if _wsgi_handler_keep_alive_patched.is_set():
        return
    _wsgi_handler_keep_alive_patched.set()

    # Patch Django's HTTP server to support keep-alive connections.
    from django.core.servers.basehttp import ServerHandler, WSGIRequestHandler
    original_handle_error = ServerHandler.handle_error
    original_close = ServerHandler.close

    def handle_error(self):
        if not self.request_handler.close_connection:
            self.request_handler.close_connection = True
        original_handle_error(self)

    def close(self):
        try:
            if not self.request_handler.close_connection:
                if self.headers and self.headers.get('connection') == 'close':
                    self.request_handler.close_connection = True
        finally:
            original_close(self)

    ServerHandler.handle_error = handle_error
    ServerHandler.close = close

    original_wsgi_handle = WSGIRequestHandler.handle

    def wsgi_handle(self):
        self.close_connection = True
        original_wsgi_handle(self)
        while not self.close_connection:
            original_wsgi_handle(self)

    WSGIRequestHandler.handle = wsgi_handle
