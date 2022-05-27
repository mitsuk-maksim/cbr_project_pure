from django.contrib import admin

from result.models import Result, ParameterValueClass, SolutionPredictValueClass

admin.site.register(Result)
admin.site.register(ParameterValueClass)
admin.site.register(SolutionPredictValueClass)
