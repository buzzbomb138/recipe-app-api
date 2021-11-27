from rest_framework import serializers

from core.models import Tags, Ingredients, Recipes


class TagsSerializer(serializers.ModelSerializer):
    """serializer for tag objects"""

    class Meta:
        model = Tags
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):
    """serializer for ingredient objects"""

    class Meta:
        model = Ingredients
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipesSerializer(serializers.ModelSerializer):
    """serialize a recipe"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredients.objects.all())
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tags.objects.all())

    class Meta:
        model = Recipes
        fields = ('id', 'title', 'ingredients', 'tags',
                  'time_minutes', 'price', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipesSerializer):
    """serialize a recipe detail"""

    ingredients = IngredientsSerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to recipes"""

    class Meta:
        model = Recipes
        fields = ('id', 'image')
        read_only_fields = ('id',)
