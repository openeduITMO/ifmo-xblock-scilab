from django.contrib import admin
from xblock_scilab.models import ScilabSubmission


class ScilabSubmissionAdmin(admin.ModelAdmin):
    list_display = ('course', 'module', 'user', 'filename', 'status',)
    list_filter = ('course', 'status',)
    search_fields = ('course', 'module', 'user', 'filename', 'status', 'sha1',)

admin.site.register(ScilabSubmission, ScilabSubmissionAdmin)