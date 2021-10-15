from django.contrib import admin

from .models import Solution, SolutionValue, ParameterValue, Parameter, Result, DataSet


admin.site.register(Solution)
admin.site.register(SolutionValue)
admin.site.register(ParameterValue)
admin.site.register(Parameter)
admin.site.register(Result)
admin.site.register(DataSet)
