from django.contrib.auth.models import User
from django.forms import ValidationError
from rest_framework import serializers



from advertisements.models import Advertisement, Favorites


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    
    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        if self.context["request"].method == 'POST':
            if len(Advertisement.objects.filter(creator__id = self.context["request"].user.id) & Advertisement.objects.filter(status='OPEN')) > 5:
                raise ValidationError('Превышен лимит открытых обьявлений, максимум = 5')

        return data
    
class FavoritesSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    advertisement = AdvertisementSerializer(read_only=True)
    
    class Meta:
        model = Favorites
        fields = ('id', 'user' , 'advertisement')
        
    def validate(self, data):
        if Advertisement.objects.get(id=data['advertisement'].id).creator == data['user']:
            raise ValidationError('Свое обьявление нельзя в избранное')
        if Favorites.objects.filter(advertisement = data['advertisement'],user = data['user']):
            raise ValidationError('такое обьявление уже есть в избранном')
        return data
        