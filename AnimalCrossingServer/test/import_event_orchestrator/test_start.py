import logging

from import_event_orchestrator.start import configure_logging


def test_should_enable_debug_logging_for_orchestrator_logger() -> None:
    # given
    logger = logging.getLogger("import_event_orchestrator.villager_import_orchestrator")

    # when
    configure_logging()

    # then
    assert logger.getEffectiveLevel() == logging.DEBUG
