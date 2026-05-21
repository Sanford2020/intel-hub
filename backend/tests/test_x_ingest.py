from app.modules.ingest.x_parser import parse_x_username


def test_parse_x_username_at_handle() -> None:
    assert parse_x_username("@OSINTdefender") == "OSINTdefender"


def test_parse_x_username_bare_handle() -> None:
    assert parse_x_username("bellingcat") == "bellingcat"


def test_parse_x_username_profile_url() -> None:
    assert parse_x_username("https://x.com/CISAgov") == "CISAgov"
    assert parse_x_username("https://twitter.com/AP/status/1") == "AP"
