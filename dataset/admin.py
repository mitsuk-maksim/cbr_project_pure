from django.contrib import admin

from .models import Solution, SolutionValue, ParameterValue, Parameter, Dataset


admin.site.register(Solution)
admin.site.register(SolutionValue)
admin.site.register(ParameterValue)
admin.site.register(Parameter)
admin.site.register(Dataset)
