from rest_framework import viewsets

from .models import Stock
from .serializers import StockSerializer


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """A ViewSet for handling read-only operations on Stock instances."""

    queryset = Stock.objects.all()
    serializer_class = StockSerializer
