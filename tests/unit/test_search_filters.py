from app.presentation.bot.routers.search import _parse_filters


def test_parse_brand_filter() -> None:
    result = _parse_filters("brand:apple")
    assert result["brand_slug"] == "apple"
    assert result["query"] is None


def test_parse_combined_filters() -> None:
    result = _parse_filters("brand:samsung price:300-600 ram:8")
    assert result["brand_slug"] == "samsung"
    assert result["min_price"] == 300.0
    assert result["max_price"] == 600.0
    assert result["min_ram_gb"] == 8


def test_parse_name_with_filters() -> None:
    result = _parse_filters("brand:apple price:500-1000 Galaxy")
    assert result["brand_slug"] == "apple"
    assert result["query"] == "Galaxy"
