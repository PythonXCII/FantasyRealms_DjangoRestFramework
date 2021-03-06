from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import GameSerializer, UserSerializer, DealSerializer
from .models import Game, Deal, Point
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.http.response import HttpResponseNotAllowed, HttpResponseNotFound
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer

    def get_queryset(self):
        games = Game.objects.filter(authorization=self.request.headers['authorization'][6:]).order_by('-id')
        return games

    def create(self, request, *args, **kwargs):
        token = Token.objects.get(key=request.headers['authorization'][6:])
        game = Game.objects.create(login=request.data['login'],
                                   password=request.data['password'], admin=token)
        game.authorization.add(token)

        Deal.objects.create(count=1, game=game)
        serializer = GameSerializer(game, many=False)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def join(self, request, *args, **kwargs):
        try:
            game = Game.objects.get(login=request.data['login'])
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Game not found!')
        if game.password == request.data['password']:
            token = Token.objects.get(key=request.headers['authorization'][6:])
            game.authorization.add(token)
            serializer = GameSerializer(game, many=False)
            return Response(serializer.data)
        else:
            return HttpResponseNotAllowed('Wrong password!')

    @action(detail=True, methods=['post'])
    def new_deal(self, request, *args, **kwargs):
        instance = self.get_object()
        deal = instance.deals.all().order_by('-count')[0]
        print(len(deal.points.all()))
        print(len(instance.authorization.all()))
        if len(deal.points.all()) == len(instance.authorization.all()):
            count = deal.count + 1
            Deal.objects.create(count=count, game=instance)
            serializer = GameSerializer(instance, many=False)
            return Response(serializer.data)
        else:
            return HttpResponseNotAllowed('Not Allowed')

    @action(detail=True, methods=['post'])
    def add_points(self, request, *args, **kwargs):
        instance = self.get_object()
        deal = instance.deals.all().order_by('-count')[0]
        user = Token.objects.get(key=request.headers['authorization'][6:]).user
        points = request.data['points']
        try:
            Point.objects.create(points=points, user=user, deal=deal)
        except IntegrityError:
            edit = Point.objects.get(user=user, deal=deal)
            edit.points = points
            edit.save()
        serializer = GameSerializer(instance, many=False)
        return Response(serializer.data)
