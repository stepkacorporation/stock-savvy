import celery

from django.db import IntegrityError
from django.db.backends.postgresql.psycopg_any import DateTimeRange
from django.core.exceptions import ValidationError
from celery.utils.log import get_task_logger
from moexalgo import Market
from requests.exceptions import RequestException
from time import perf_counter
from datetime import date

from core.celery import app, add_file_logger
from .utils.task_utils import get_available_dates, load_candles, get_div_pay
from .models import Stock, Candle, Dividend

logger = add_file_logger(get_task_logger(__name__))


def load_stock_data() -> None:
    """
    Runs tasks to load available stocks, dividend payments and
    historical data for all loaded available stocks.

    Returns:
        None
    """

    logger.info('The start of load stock data')
    _start_time = perf_counter()

    loaded_available_stocks = load_available_stocks.delay()
    loaded_available_stocks.get()  # Waiting for the result of loading the available stocks

    loaded_div_pay = load_div_pay.delay()

    stocks = Stock.objects.all()
    tasks_group = celery.group(load_historical_data_for_ticker.s(stock.ticker) for stock in stocks)()
    tasks_group.get()  # Waiting for the result of loading historical data for all stocks

    loaded_div_pay.get()  # Waiting for the result of loading dividend payments for all stocks

    logger.info(f'Stock data has been successfully loaded in {perf_counter() - _start_time}s')


@app.task
def load_available_stocks() -> int:
    """
    Loads available stocks from the market and creates or updates Stock objects in the database.

    Returns:
         int: The number of Stock objects created.
    """

    logger.info('The start of load available stocks')
    _start_time = perf_counter()

    try:
        stocks: list[dict] = Market('stocks').tickers()
    except RequestException as error:
        logger.error(f'RequestException occurred: {error}', exc_info=True)
        return 0
    except Exception as error:
        logger.error(f'An unexpected error occurred: {error}', exc_info=True)
        return 0
    else:
        logger.debug(f'Information about the stocks was received successfully. {stocks=}')

    stock_objects = []
    for stock in stocks:
        try:
            stock_objects.append(Stock(
                ticker=stock.get('SECID'),
                shortname=stock.get('SHORTNAME'),
                secname=stock.get('SECNAME'),
                latname=stock.get('LATNAME'),
                prevprice=stock.get('PREVPRICE'),
                lotsize=stock.get('LOTSIZE'),
                facevalue=stock.get('FACEVALUE'),
                faceunit=stock.get('FACEUNIT'),
                status=stock.get('STATUS'),
                decimals=stock.get('DECIMALS'),
                minstep=stock.get('MINSTEP'),
                prevdate=stock.get('PREVDATE'),
                issuesize=stock.get('ISSUESIZE'),
                isin=stock.get('ISIN'),
                regnumber=stock.get('REGNUMBER'),
                prevlegalcloseprice=stock.get('PREVLEGALCLOSEPRICE'),
                currencyid=stock.get('CURRENCYID'),
                sectype=stock.get('SECTYPE'),
                listlevel=stock.get('LISTLEVEL'),
                settledate=stock.get('SETTLEDATE'),
            ))
        except ValidationError as error:
            logger.error(f'ValidationError occurred for {stock=}: {error}', exc_info=True)
        except Exception as error:
            logger.error(f'An error occurred while creating a Stock instance with {stock=}: {error}',
                         exc_info=True)
            return 0
        else:
            logger.debug(f'Stock objects have been successfully created. {stock_objects=}')

    try:
        Stock.objects.bulk_create(
            stock_objects,
            update_conflicts=True,
            unique_fields=['ticker'],
            update_fields=[
                'shortname', 'secname', 'latname', 'prevprice', 'lotsize', 'facevalue', 'faceunit',
                'status', 'decimals', 'minstep', 'prevdate', 'issuesize', 'isin', 'regnumber',
                'prevlegalcloseprice', 'currencyid', 'sectype', 'listlevel', 'settledate', 'updated',
            ],
        )
    except IntegrityError as error:
        logger.error(f'Integrity error occurred: {error}', exc_info=True)
        return 0
    except Exception as error:
        logger.error(f'An error occurred during bulk creation: {error}', exc_info=True)
        return 0

    loaded = len(stock_objects)
    logger.info(f'{loaded} stock records have been successfully loaded in {perf_counter() - _start_time}s')
    return loaded


@app.task
def load_div_pay(ticker: str | None = None) -> None:
    """
    Loads dividend payments for a given stock ticker or for all stocks.

    Parameters:
        ticker (str or None): The ticker symbol of the stock. If None, loads dividend payments for all stocks.

    Returns:
        None
    """

    if ticker is not None:
        _load_div_pay_for_ticker.delay(ticker)
    else:
        stocks = Stock.objects.all()
        for stock in stocks:
            _load_div_pay_for_ticker.delay(stock.ticker)


@app.task
def _load_div_pay_for_ticker(ticker: str) -> int:
    """
    Loads dividend payments for a given stock ticker into the database.

    Parameters:
        ticker (str): The ticker symbol for which dividend payments is to be loaded.

    Returns:
        int: The number of Dividend objects created.
    """

    logger.info(f'The start of load dividend payments for {ticker=}')
    _start_time = perf_counter()

    created = 0

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist as error:
        logger.error(f'Stock with {ticker=} does not exist: {error}', exc_info=True)
        return created

    div_data = get_div_pay(ticker)
    if not div_data:
        return created

    try:
        for div in div_data:
            try:
                date_ = date.fromisoformat(div[0])
                value = div[1]
            except (ValueError, IndexError) as error:
                logger.error(f'A data processing error has occurred for {ticker=}: {error}', exc_info=True)
                return created
            if not Dividend.objects.filter(stock=stock, registryclosedate=date_).exists():
                try:
                    Dividend.objects.create(stock=stock, value=value, registryclosedate=date_)
                except ValidationError as error:
                    logger.error(f'ValidationError occurred for {ticker=}: {error}', exc_info=True)
                    return created
                created += 1
    except Exception as error:
        logger.error(f'An unexpected error occured for {ticker=}: {error}', exc_info=True)
        return created
    else:
        logger.info(f'{created} dividend payment records have been successfully'
                    f' loaded for {ticker=} in {perf_counter() - _start_time}s')
        return created


@app.task
def load_historical_data_for_ticker(ticker: str) -> int:
    """
    Loads historical data for a specific stock by creating Candle objects and storing them in the database.

    Parameters:
        ticker (str): The ticker symbol for which historical data is to be loaded.

    Returns:
        int: The number of Candle objects created.
    """

    logger.info(f'The start of load historical data for {ticker=}')
    _start_time = perf_counter()
    created_candles = 0

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist as error:
        logger.error(f'Stock with {ticker=} does not exist: {error}', exc_info=True)
        return created_candles

    dates = get_available_dates(ticker)

    if dates is None:
        logger.error(f'Could not get available dates for {ticker=}')
        return created_candles

    start_date, end_date = dates

    try:
        for candle_objects in load_candles(ticker, start_date, end_date):
            created = Candle.objects.bulk_create([
                Candle(
                    stock=stock,
                    open=candle.open,
                    close=candle.close,
                    high=candle.high,
                    low=candle.low,
                    value=candle.value,
                    volume=candle.volume,
                    time_range=DateTimeRange(candle.begin, candle.end)
                )
                for candle in candle_objects
            ])
            created_candles += len(created)
    except IntegrityError as error:
        logger.error(f'Integrity error occurred for {ticker=}: {error}', exc_info=True)
        return created_candles
    except ValidationError as error:
        logger.error(f'ValidationError occurred for {ticker=}: {error}', exc_info=True)
    except Exception as error:
        logger.error(f'An error occurred while creating a Candle instance'
                     f' or during bulk creation for {ticker=}: {error}', exc_info=True)
        return created_candles
    else:
        logger.info(f'{created_candles} historical data records for the {ticker=} has been'
                    f' successfully loaded in {perf_counter() - _start_time}s')
        return created_candles
