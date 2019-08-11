""" GraphQL Schema """
import graphene
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import Review as ReviewModel
from models import AggregatedReviews as AggregatedReviewsModel


class Review(MongoengineObjectType):
    """ Individial student review. """
    class Meta:
        model = ReviewModel


class AggregatedReviews(MongoengineObjectType):
    """ Object representing aggregated reviews. """
    class Meta:
        model = AggregatedReviewsModel

class Query(graphene.ObjectType):
    """ Full-search query.

    [CURRENTLY ONLY SEARCHING ONE COLLECTION RIP]

    Please use a smaller query (n=100) to perform experiments/exploration, then
    use '..All' sparingly to retrieve the data you need. """

    reviews = graphene.List(Review, n=graphene.Int())
    reviews_all = graphene.List(Review)
    aggregated_reviews = graphene.List(AggregatedReviews, n=graphene.Int())
    aggregated_reviews_all = graphene.List(AggregatedReviews)

    def resolve_reviews(self, info, n):
        return list(ReviewModel.objects[:n])

    def resolve_reviews_all(self, info):
        return list(ReviewModel.objects.all())

    def resolve_aggregated_reviews(self, info, n):
        return list(AggregatedReviewsModel.objects[:n])

    def resolve_aggregated_reviews_all(self, info):
        return list(AggregatedReviewsModel.objects.all())

schema = graphene.Schema(query=Query, types=[Review, AggregatedReviews])
