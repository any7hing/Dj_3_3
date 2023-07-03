
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from advertisements.models import Advertisement, Favorites
from advertisements.permissions import IsOwner
from advertisements.serializers import AdvertisementSerializer, FavoritesSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User

class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_fields = ['creator','created_at']
    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsOwner()]
        return []
    

    @action(detail=True, url_path='favorites', permission_classes=[IsAuthenticated, ])
    def add_favorites_posts(self, request, pk):
        queryset = Advertisement.objects.get(id=pk)
        if queryset:
            validated_data = {'advertisement': queryset, 'user': request.user}
            serializer = FavoritesSerializer(data=validated_data)
            serializer.validate(data=validated_data)
            serializer.create(validated_data)
            return Response ('Вроде получилось')

    
    @action(detail=True,methods=['DELETE'], url_path='delete', permission_classes=[IsAuthenticated, IsOwner() ])
    def delete_favorites_posts(self, request, pk):
            
            Favorites.objects.get(advertisement__id = pk).delete()
            return Response ('Удалено...наверное')
    
    @action(detail=False, methods=['GET'], url_path='favorites_posts', permission_classes=[IsAuthenticated])
    def show_favorites_posts(self, request):
        queryset = Favorites.objects.filter(user=request.user)
        serializer = FavoritesSerializer(queryset,many=True)
        return Response(serializer.data)