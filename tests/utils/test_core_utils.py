from datetime import datetime, timezone, timedelta

from app.utils import utc_to_cst, format_datetime
from app.utils.provider_icon_mapper import get_icon_filename, extract_icon_from_url
from app.utils.response import (
    standard_response,
    success_response,
    error_response,
    not_found_response,
    unauthorized_response,
)


def test_standard_response_returns_expected_structure():
    result = standard_response(data={"k": 1}, code=201, msg="ok")
    assert result == {"code": 201, "data": {"k": 1}, "msg": "ok"}


def test_success_response_uses_200_code():
    result = success_response(data=[1, 2, 3], msg="done")
    assert result["code"] == 200
    assert result["data"] == [1, 2, 3]
    assert result["msg"] == "done"


def test_error_related_responses():
    e = error_response(msg="bad", code=422, data={"detail": "x"})
    nf = not_found_response("用户")
    un = unauthorized_response()
    assert e == {"code": 422, "data": {"detail": "x"}, "msg": "bad"}
    assert nf == {"code": 404, "data": None, "msg": "用户未找到"}
    assert un == {"code": 401, "data": None, "msg": "未授权访问"}


def test_utc_to_cst_handles_none_and_naive_datetime():
    assert utc_to_cst(None) is None
    naive = datetime(2026, 1, 1, 0, 0, 0)
    converted = utc_to_cst(naive)
    assert converted.tzinfo is not None
    assert converted.utcoffset() == timedelta(hours=8)
    assert converted.hour == 8


def test_utc_to_cst_handles_aware_utc_datetime():
    aware_utc = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    converted = utc_to_cst(aware_utc)
    assert converted.utcoffset() == timedelta(hours=8)
    assert converted.hour == 8


def test_format_datetime_handles_none_and_naive_datetime():
    assert format_datetime(None) == ""
    naive = datetime(2026, 1, 1, 0, 0, 0)
    assert format_datetime(naive, include_timezone=False) == "2026-01-01T08:00:00"


def test_format_datetime_with_timezone_output():
    cst = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    assert format_datetime(cst, include_timezone=True) == "2026-01-01T08:00:00+08:00"


def test_get_icon_filename_returns_mapped_or_default():
    assert get_icon_filename("openai") == "openai.svg"
    assert get_icon_filename("unknown_vendor") == "unknown_vendor.svg"


def test_extract_icon_from_url_covers_happy_and_boundary_paths():
    assert extract_icon_from_url(None, "openai") == "openai.svg"
    assert extract_icon_from_url("abc.txt", "openai") == "openai.svg"
    assert extract_icon_from_url("https://example.com/icons/x.svg", "openai") == "x.svg"
    assert extract_icon_from_url("https://example.com/icons/x.png", "openai") == "openai.svg"
    assert extract_icon_from_url("custom.svg", "openai") == "custom.svg"
    assert extract_icon_from_url("custom.png", "openai") == "openai.svg"
