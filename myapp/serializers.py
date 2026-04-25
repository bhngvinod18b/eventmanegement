from rest_framework import serializers
from .models import Myevent, Bookevent, Like, Follow, Saved_event
from rest_framework import serializers
from django.contrib.auth.models import User


class Myeventserializers(serializers.ModelSerializer):
    class Meta:
        model = Myevent
        fields = '__all__'
        
class Bookeventserializers(serializers.ModelSerializer):
    class Meta:
        model = Bookevent
        fields = '__all__'
class Likeserializers(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
class Followserializers(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'
class Saved_eventserializers(serializers.ModelSerializer):
    class Meta:
        model = Saved_event
        fields = '__all__'
        