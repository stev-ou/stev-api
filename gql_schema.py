""" GraphQL Schema """
import graphene
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import Review as ReviewModel
from models import AggregatedReviews as AggregatedReviewsModel

class Review(MongoengineObjectType):

    class Meta:
        model = ReviewModel

class AggregatedReviews(MongoengineObjectType):

    class Meta:
        model = AggregatedReviewsModel

class Query(graphene.ObjectType):
    reviews = graphene.List(Review)
    aggregated_reviews = graphene.List(AggregatedReviews)

    def resolve_reviews(self, info):
        return list(ReviewModel.objects[:100])

    def resolve_aggregated_reviews(self, info):
        return list(AggregatedReviewsModel.objects[:100])

schema = graphene.Schema(query=Query, types=[Review, AggregatedReviews])
