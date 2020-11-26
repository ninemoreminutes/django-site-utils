# Django
from django.contrib import admin


class InlineSelectRelatedMixin(object):

    inline_select_related = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.inline_select_related:
            qs = qs.select_related(*self.inline_select_related)
        return qs


class InlinePrefetchRelatedMixin(object):

    inline_prefetch_related = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.inline_prefetch_related:
            qs = qs.prefetch_related(*self.inline_prefetch_related)
        return qs


class InlineMixins(InlineSelectRelatedMixin, InlinePrefetchRelatedMixin):
    pass


class StackedInline(InlineMixins, admin.StackedInline):
    pass


class TabularInline(InlineMixins, admin.TabularInline):
    pass


class AdminAddChangeDeleteMixin(object):

    can_add = True
    can_change = True
    can_delete = True

    def has_add_permission(self, request):
        return super().has_add_permission(request) if self.can_add else False

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) if self.can_change else False

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) if self.can_delete else False


class AdminListPrefetchRelatedMixin(object):

    list_prefetch_related = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.list_prefetch_related:
            qs = qs.prefetch_related(*self.list_prefetch_related)
        return qs


class AdminAddFormMixin(object):

    add_form = None

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and self.add_form:
            kwargs.setdefault('form', self.add_form)
        return super().get_form(request, obj, **kwargs)


class AdminAddViewFieldsMixin(object):

    add_fields = None
    add_fieldsets = None
    view_fields = None
    view_fieldsets = None

    def get_fields(self, request, obj=None):
        if obj is None and self.add_fields is not None:
            return self.add_fields
        elif obj is not None and self.view_fields is not None and not self.has_change_permission(request, obj):
            return self.view_fields
        else:
            return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if obj is None and self.add_fieldsets is not None:
            return self.add_fieldsets
        elif obj is not None and self.view_fieldsets is not None and not self.has_change_permission(request, obj):
            return self.view_fieldsets
        else:
            return super().get_fieldsets(request, obj)


class AdminAddViewInlinesMixin(object):

    add_inlines = None
    view_inlines = None

    def get_inlines(self, request, obj=None):
        if obj is None and self.add_inlines is not None:
            return self.add_inlines
        elif obj is not None and self.view_inlines is not None and not self.has_change_permission(request, obj):
            return self.view_inlines
        else:
            return self.inlines

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.get_inlines(request, obj):
            inline = inline_class(self.model, self.admin_site)
            if request:
                inline_has_add_permission = inline.has_add_permission(request, obj)
                if not inline.has_view_or_change_permission(request, obj):
                    continue
                if not inline_has_add_permission:
                    inline.max_num = 0
            inline_instances.append(inline)
        return inline_instances


class AdminMixins(AdminAddChangeDeleteMixin, AdminListPrefetchRelatedMixin, AdminAddFormMixin, AdminAddViewFieldsMixin, AdminAddViewInlinesMixin):
    pass


class ModelAdmin(AdminMixins, admin.ModelAdmin):
    pass
