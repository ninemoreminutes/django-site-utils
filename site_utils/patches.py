# Python
import threading

_runserver_addrport_patched = threading.Event()


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
