import graphene
from graphene_django.types import ErrorType


class ErrorMutationMixin(object):
    ok = graphene.Boolean()
    errors = graphene.List(ErrorType)

    def resolve_ok(self, info):
        return not self.errors or not len(self.errors)

    def resolve_errors(self, info):
        return self.errors or []


class CustomMutation(graphene.Mutation, ErrorMutationMixin):
    validators = dict()

    class Meta:
        abstract = True

    @classmethod
    def Field(
            cls, name=None, description=None, deprecation_reason=None, required=False
    ):
        """ Mount instance of mutation Field. """
        return Field(
            cls._meta.output,
            args=cls._meta.arguments,
            resolver=decorate_mutate_func(cls._meta.resolver, cls),
            name=name,
            description=description or cls._meta.description,
            deprecation_reason=deprecation_reason,
            required=required,
        )

    @classmethod
    def mutate(cls, root, info):
        return cls(ok=True, errors=[])