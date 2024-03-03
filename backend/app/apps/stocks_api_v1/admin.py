from django.contrib import admin

from .models import Stock, Candle


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    The stock's admin panel.
    """

    pass


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    """
    The candle's admin panel.
    """

    list_display = ('stock', 'open', 'close', 'high', 'low', 'value', 'volume', 'time_range')

