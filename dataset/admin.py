from django import forms
from django.contrib import admin
from django.contrib.admin import display

from .models import Solution, SolutionValue, ParameterValue, Parameter, Dataset


class SolutionInline(admin.TabularInline):
    model = Solution
    exclude = ('is_active',)
    extra = 0
    can_delete = False
    show_full_result_count = True
    show_change_link = True


class ParameterInline(admin.TabularInline):
    model = Parameter
    exclude = ('is_active',)
    extra = 0
    # show_change_link = True
    show_change_link = True
    can_delete = False

    # raw_id_fields = ('dataset',)
    # raw_id_fields = ("",)


class DatasetPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user')
    # list_per_page = 10
    inlines = [ParameterInline, SolutionInline]

    # raw_id_fields = ('parameters',)
    # list_display_links = ('title',)

    # readonly_fields = ('get_parameters', ParameterInline, SolutionInline)

    @display(ordering='parameters', description='Author')
    def get_parameters(self, obj):
        return obj.parameters.all()


class SolutionValueInline(admin.TabularInline):
    model = SolutionValue
    exclude = ('is_active',)
    extra = 1
    can_delete = False
    raw_id_fields = ('solution',)
    autocomplete_fields = ('solution',)
    # show_full_result_count = True


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    exclude = ('is_active',)
    extra = 1
    raw_id_fields = ('solution_value', 'parameter')
    readonly_fields = ('solution_value', 'parameter')
    autocomplete_fields = ('solution_value', 'parameter')
    # show_change_link = True
    can_delete = False


class ParameterPageAdmin(admin.ModelAdmin):
    # list_display = ('id', 'title')
    inlines = [ParameterValueInline]
    search_fields = ['title']
    raw_id_fields = ('dataset',)


class SolutionPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ['title']
    inlines = [SolutionValueInline]


class SolutionValuePageAdmin(admin.ModelAdmin):
    # list_display = ('id', 'title')
    # raw_id_fields = ('solution',)
    search_fields = ('value',)
    list_per_page = 10


#
# class ParameterValuePageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'value')
#     list_per_page = 5


admin.site.register(Solution, SolutionPageAdmin)
admin.site.register(SolutionValue, SolutionValuePageAdmin)
admin.site.register(ParameterValue)
admin.site.register(Parameter, ParameterPageAdmin)
admin.site.register(Dataset, DatasetPageAdmin)
