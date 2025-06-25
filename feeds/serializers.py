from rest_framework import serializers
from .models import Announcement, Event, Post, Like, Comment
from datetime import datetime

class AnnouncementSerializer(serializers.ModelSerializer):
    acknowledged_count = serializers.SerializerMethodField()
    def get_acknowledged_count(self, obj):
        return obj.acknowledge_users.count()
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def get_is_completed(self, obj):
        event_datetime = datetime.combine(obj.date, obj.time)
        return event_datetime < datetime.now()
    


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'post']

class PostSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    acknowledged_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.liked_users.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_liked(self, obj):
        return obj.liked_users.values_list('id', flat=True)
    
    def get_acknowledged_count(self, obj):
        return obj.acknowledge_users.count()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['comments'] = sorted(representation['comments'], key=lambda x: x['created_at'], reverse=True)
        return representation

    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['user']
