import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def _format_message(line, message):
    if line:
            return str(line) + ': ' + message
    else:
        return message


def warning(line, message):
    logger.warning(_format_message(line, message))


def error(line, message):
    logger.error(_format_message(line, message))


def debug(line, message):
    logger.debug(_format_message(line, message))


def info(line, message):
    logger.info(_format_message(line, message))