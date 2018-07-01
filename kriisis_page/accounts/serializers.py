import djoser.serializers
from hashid_field.rest import HashidSerializerCharField


class UserCreateSerializer(djoser.serializers.UserCreateSerializer):
    id = HashidSerializerCharField(read_only=True)
