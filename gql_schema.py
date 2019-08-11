""" GraphQL Schema """
import graphene
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import Review as ReviewModel
from models import AggReview as AggReviewModel

class Review(MongoengineObjectType):

    class Meta:
        model = ReviewModel

class AggReview(MongoengineObjectType):

    class Meta:
        model = AggReviewModel

class Query(graphene.ObjectType):
    reviews = graphene.List(Review)

    def resolve_reviews(self, info):
    	return list(ReviewModel.objects.all())

schema = graphene.Schema(query=Query, types=[Review, AggReview])
