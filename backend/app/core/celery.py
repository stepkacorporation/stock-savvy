import os
import celery.signals

from .utils.logger import add_file_logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = celery.Celery('stocks', broker_connection_retry=False, broker_connection_retry_on_startup=True)
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()


@celery.signals.after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    """Adds a file logger setup function to the Celery logger after setup signal."""

    logger = add_file_logger(logger)
    return logger
