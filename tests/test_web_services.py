import pytest
import logging
from typing import Tuple

from fcms_web_services import split_tag, get_newer_release

def _get_dummy_logger():
    logger = logging.getLogger("dummy")
    logger.addHandler(logging.NullHandler())
    return logger

@pytest.mark.parametrize(
    "tag, expected_result",
    [
        ("v1.0", (1, 0)),
        ("v1.1.2", (1, 1, 2)),
        ("v0.15", (0, 15)),
        ("v9", (9,))
    ]
)
def test_split_tag(tag:str, expected_result:Tuple[int]):
    assert split_tag(tag) == expected_result

#@pytest.mark.skip(reason="Potentially long-running or external test")
def test_get_newer_release():
    assert get_newer_release(_get_dummy_logger(), "anthonylangsworth", "FCMS", (0, 3))
