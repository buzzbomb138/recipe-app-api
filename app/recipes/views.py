from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tags, Ingredients, Recipes
from . import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """create a new tag"""
        serializer.save(user=self.request.user)


class TagsViewSet(BaseRecipeAttrViewSet):
    """manage tags in the database"""
    queryset = Tags.objects.all()
    serializer_class = serializers.TagsSerializer


class IngredientsViewSet(BaseRecipeAttrViewSet):
    """manage ingredients in the database"""
    queryset = Ingredients.objects.all()
    serializer_class = serializers.IngredientsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """manage recipes in the database"""
    serializer_class = serializers.RecipesSerializer
    queryset = Recipes.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class
