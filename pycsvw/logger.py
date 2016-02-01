import logging

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def _format_message(line, message, args):
    if line:
        message = str(line) + ': ' + message
    for arg in args:
        try:
            message += str(arg) + ','
        except Exception:
            pass
    return message


def warning(line, message, *args):
    logger.warning(_format_message(line, message, args))


def error(line, message, *args):
    logger.error(_format_message(line, message, args))


def debug(line, message, *args):
    logger.debug(_format_message(line, message, args))


def info(line, message, *args):
    logger.info(_format_message(line, message, *args))
