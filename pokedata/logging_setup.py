"""Configuracao central de logging. So' usado pra diagnostico (cache,
rede, progresso interno) -- o relatorio em si continua saindo por print(),
porque esse e' o produto final do script, nao um log de debug.
"""
import logging

LOGGER_NAME = "pokedata"


def configure(verbose=False):
    """Liga o logger do projeto. Nivel INFO com --verbose, WARNING (so'
    problema) por padrao."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    return logger


def get_logger():
    return logging.getLogger(LOGGER_NAME)
