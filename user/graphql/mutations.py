import graphene

from cbr_project_pure.functions import CustomMutation


class RegistrationInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class Registration(CustomMutation):

    class Arguments:
        input = RegistrationInput(required=True)

    @classmethod
    def mutate(cls, root, info, input: RegistrationInput):

        return cls(ok=True, errors=[])




class Mutations(graphene.ObjectType):
    registration = Registration.Field()
