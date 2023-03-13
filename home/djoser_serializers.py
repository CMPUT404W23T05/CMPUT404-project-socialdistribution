# Copyright 2023 John Macdonald, Elena Xu, Jonathan Lo, Gurkirat Singh, and Geoffery Banh

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#         http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from rest_framework import serializers
from .models import *
from .serializers import AuthorSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'author', 'auth_token')
        read_only_fields = ('auth_token',)

    def get_author(self, obj):
        try:
            author = obj.author
        except Author.DoesNotExist:
            author = None

        return AuthorSerializer(author).data
