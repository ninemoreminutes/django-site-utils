# Python
from __future__ import unicode_literals

__all__ = ['handler400', 'handler403', 'handler404', 'handler500']


handler400 = 'site_utils.views.handle_400'
handler403 = 'site_utils.views.handle_403'
handler404 = 'site_utils.views.handle_404'
handler500 = 'site_utils.views.handle_500'
