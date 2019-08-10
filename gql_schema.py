""" GraphQL Schema """
import graphene
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import Review as ReviewModel
from models import AggReview as AggReviewModel

class Review(MongoengineObjectType):

    class Meta:
        model = ReviewModel
        interfaces = (Node,)

class AggReview(MongoengineObjectType):

    class Meta:
        model = AggReviewModel
        interfaces = (Node,)

class Query(graphene.ObjectType):
    node = Node.Field()
    all_reviews = MongoengineConnectionField(Review)

schema = graphene.Schema(query=Query, types=[Review, AggReview])
