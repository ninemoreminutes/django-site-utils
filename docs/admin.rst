Admin Mixins
============

Django Site Utils provides mixin and base classes to extend the built-in capabilities of the Django admin. By default,
these mixins should not alter the behavior of the Django admin in any way unless they are configured via the model admin
class attributes documented below.

InlineSelectRelatedMixin
------------------------

This mixin allows use of ``select_related`` on inline admin classes via the ``inline_select_related`` attribute::

    class MyInline(InlineSelectRelatedMixin, admin.TabularInline):

        inline_select_related = ('related_model',)

InlinePrefetchRelatedMixin
--------------------------

This mixin allows use of ``prefetch_related`` on inline admin classes via the ``inline_prefetch_related`` attribute::

    class MyInline(InlinePrefetchRelatedMixin, admin.TabularInline):

        inline_prefetch_related = ('related_m2m_model',)

InlineMixins
------------

This mixin class combines all of the inline mixin classes provided by Django Site Utils.

StackedInline
-------------

This class combines ``InlineMixins`` with Django's default ``StackedInline`` admin class.

TabularInline
-------------

This class combines ``InlineMixins`` with Django's default ``TabularInline`` admin class.

AdminAddChangeDeleteMixin
-------------------------

This mixin adds the ability to disable all add, change or delete operations for the given ``ModelAdmin`` via class
attributes. When allowed, the normal Django permissions will still be checked. When disabled, the given operation is
never allowed, even for superusers. The following example defines a view-only admin class::

    class MyModelAdmin(AdminAddChangeDeleteMixin, admin.ModelAdmin):

        can_add = False
        can_change = False
        can_delete = False

AdminListPrefetchRelatedMixin
-----------------------------

This mixin allows use of ``prefetch_related`` on admin classes via the ``list_prefetch_related`` attribute::

    class MyModelAdmin(AdminListPrefetchRelatedMixin, admin.ModelAdmin):

        list_prefetch_related = ('related_m2m_model',)

AdminAddFormMixin
-----------------

This mixin allows for use of a different form class when adding a new instance than the form used for changing an
existing instance::

    class MyModelAdmin(AdminAddFormMixin, admin.ModelAdmin):
    
        add_form = MyModelAddForm

AdminAddViewFieldsMixin
-----------------------

This mixin allows for different fields and fieldsets to be used for add or view operations than for
change operations. Similarly to how ``fieldsets`` and ``fields`` work, if ``add_fieldsets`` or ``view_fieldsets`` are
specified, they take precedence over ``add_fields`` and ``view_fields``, respectively::

    class MyModelAdmin(AdminAddViewFieldsMixin, admin.ModelAdmin):
    
        add_fields = ('name', 'slug',)
        view_fields = ('name_view', 'slug_view',)
        add_fieldsets = ...
        view_fieldsets = ...

AdminAddViewInlinesMixin
------------------------

This mixin allows for different inlines to be displayed for add and view operations than for change operations. The
following example displays no inlines when adding a new instance, and a custom inline when the user is only allowed to
view the model::

    class MyModelAdmin(AdminAddViewInlinesMixin, admin.ModelAdmin):
  
        add_inlines = []
        view_inlines = [ViewRelatedInline]

AdminMixins
-----------

This mixin class combines all of the model admin mixin classes provided by Django Site Utils.

ModelAdmin
----------

This class combines ``AdminMixins`` with Django's default ``ModelAdmin`` admin class.
