from rest_framework import serializers
from ticket.models import Ticket, Category

class TicketSerializer(serializers.ModelSerializer):
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # assigned_user = serializers.ReadOnlyField(source='assigned_user.username')
    # category = serializers.CharField(source="category.parent_name", read_only=True)
    # sub_category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_at','updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate(self, data):
        """Ensure parent_name exists and is not the same as the category name."""
        name = data.get('name')
        parent_name = data.get('parent_name')

        if parent_name:
            # Check if the parent exists
            if not Category.objects.filter(name=parent_name).exists():
                raise serializers.ValidationError({"parent_name": "Parent category does not exist."})
            
            # Check if a category is being set as its own parent
            if name == parent_name:
                raise serializers.ValidationError({"parent_name": "A category cannot be its own parent."})

        return data

