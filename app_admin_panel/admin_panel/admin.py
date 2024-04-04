from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from import_export.resources import ModelResource
from admin_panel.models import User, Advertisement, Dispatcher, Post


class CustomImportExport(ImportExportModelAdmin, ExportActionModelAdmin):
    pass


# setup import
class UserResource(ModelResource):
    class Meta:
        model = User
        import_id_fields = ('user_id',)


@admin.register(User)
class UserAdmin(CustomImportExport):
    resource_classes = [UserResource]
    list_display = ('id', 'user_id', 'username', 'inst_username', 'status', 'is_banned', 'link', 'created_at')
    list_display_links = ('user_id', )
    list_editable = ('status', 'username', 'is_banned')


@admin.register(Advertisement)
class AdvertisementAdmin(CustomImportExport):
    list_display = [field.name for field in Advertisement._meta.fields if field.name not in ['photo_file_id', 'video_file_id', 'document_file_id']]
    list_editable = ('is_approved_by_bloger', 'is_paid', 'is_rejected', 'agency', 'manager', 'bloger', 'buyer')


@admin.register(Dispatcher)
class OrderAdmin(CustomImportExport):
    list_display = [field.name for field in Dispatcher._meta.fields]


@admin.register(Post)
class OrderAdmin(CustomImportExport):
    list_display = [field.name for field in Post._meta.fields]
    list_editable = [field.name for field in Post._meta.fields if field.name != 'id' and field.name != 'created_at']


# sort models from admin.py by their registering (not alphabetically)
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = list(app_dict.values())
    return app_list


admin.AdminSite.get_app_list = get_app_list
