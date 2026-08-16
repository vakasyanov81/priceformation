"""tests for price grouping key helpers."""

from typing import Any

import pytest

from parsers.common_price_group_key import clear_model, define_intimacy, group_key, sanitize_value
from parsers.row_item.row_item import RowItem


def _row(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "title": "no marker",
        "type_production": "легковая",
        "diameter": "16",
    }
    payload.update(fields)
    return RowItem(payload)


def test_sanitize_none() -> None:
    assert sanitize_value([None, 1]) == ("", "1")


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (None, ""),
        ("", ""),
        ("КАМА-NU 701", "nu701"),
        ("NU701", "nu701"),
        ("NU 701", "nu701"),
        ("A-B-C", "a-b-c"),
        ("PW-1", "pw-1"),
        ("PS-1", "ps-1"),
        ("CW-2", "cw-2"),
        ("CA-2", "ca-2"),
        ("Кама-1260-1", "1260-1"),
        ("Кама-1260-2", "1260-2"),
        ("Кама", ""),
        ("SNOW CROSS 2", "snowcross2"),
        ("Snow Cross 2", "snowcross2"),
        ("KAMAZ-X", "kamaz-x"),
    ],
)
def test_clear_model(model: str | None, expected: str) -> None:
    assert clear_model(model) == expected


def test_clear_model_kama_nu_variants_match() -> None:
    assert clear_model("КАМА-NU 701") == clear_model("NU701") == clear_model("NU 701")


def test_clear_model_distinct_hyphen_suffixes() -> None:
    assert clear_model("PW-1") != clear_model("PS-1")
    assert clear_model("CW-2") != clear_model("CA-2")
    assert clear_model("Кама-1260-1") != clear_model("Кама-1260-2")


def test_clear_model_strips_manufacturer() -> None:
    assert clear_model("НКШЗ-NU701", "НКШЗ") == "nu701"
    assert clear_model("НКШЗ", "НКШЗ") == ""


def test_clear_model_strips_brand() -> None:
    assert clear_model("Brand PW-1", brand="Brand") == "pw-1"


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("tyre TL extra", "TL"),
        ("tyre tt extra", "TT"),
        ("tyre TTF extra", "TTF"),
    ],
)
def test_intimacy_from_title_word(title: str, expected: str) -> None:
    assert define_intimacy(_row(title=title)) == expected


def test_intimacy_requires_separate_word() -> None:
    assert define_intimacy(_row(title="TLextra")) is None


def test_intimacy_truck_float_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22.5")
    assert define_intimacy(row) == "TL"


def test_intimacy_truck_comma_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22,5")
    assert define_intimacy(row) == "TL"


def test_intimacy_truck_integer_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22")
    assert define_intimacy(row) is None


def test_intimacy_not_truck_float_diameter() -> None:
    row = _row(type_production="легковая", diameter="22.5")
    assert define_intimacy(row) is None


def test_intimacy_invalid_diameter() -> None:
    row = _row(type_production="грузовая", diameter="xx")
    assert define_intimacy(row) is None


def test_group_key_hides_matching_brand() -> None:
    shared = {"manufacturer_name": "НКШЗ", "model": "X"}
    same_brand = RowItem({**shared, "brand": "НКШЗ"})
    blank_brand = RowItem(shared)
    other_brand = RowItem({**shared, "brand": "Other"})

    assert group_key(same_brand) == group_key(blank_brand)
    assert group_key(same_brand) != group_key(other_brand)


def test_group_key_empty_manufacturer_and_type() -> None:
    key = group_key(_row(manufacturer_name="", type_production=""))
    assert "xxxx" not in key


def test_group_key_type_production_lower() -> None:
    key = group_key(_row(type_production="Легковая"))
    assert "легковая" in key
    assert "ЛЕГКОВАЯ" not in key


def test_group_key_tl_matches_missing_intimacy() -> None:
    assert group_key(_row(intimacy="TL")) == group_key(_row())
    assert group_key(_row(title="tyre TL extra")) == group_key(_row())
    assert group_key(_row(camera_type="TL")) == group_key(_row())


def test_group_key_tt_differs_from_tl() -> None:
    assert group_key(_row(intimacy="TT")) != group_key(_row(intimacy="TL"))
    assert group_key(_row(title="tyre TT extra")) != group_key(_row(title="tyre TL extra"))


def test_group_key_ttf_differs_from_tt() -> None:
    assert group_key(_row(intimacy="TTF")) != group_key(_row(intimacy="TT"))


def test_group_key_ignores_axis() -> None:
    assert group_key(_row(axis="Рулевая")) == group_key(_row())


def test_group_key_includes_cleared_model() -> None:
    assert "nu701" in group_key(_row(model="КАМА-NU 701"))


_KAMA_ALIASES = {
    "НКШЗ": ["НК.ШЗ", "Нк.шз", "Кама", "Kama"],
    "Aeolus": ["Аеолус"],
    "Triangle": [],
}


def test_group_key_nkshz_matches_kama() -> None:
    nkshz = _row(manufacturer_name="НКШЗ", model="NU701")
    kama = _row(manufacturer_name="Кама", model="NU 701")
    assert group_key(nkshz, _KAMA_ALIASES) == group_key(kama, _KAMA_ALIASES)


def test_group_key_nkshz_not_triangle() -> None:
    nkshz = _row(manufacturer_name="НКШЗ", model="NU701")
    triangle = _row(manufacturer_name="Triangle", model="NU701")
    assert group_key(nkshz, _KAMA_ALIASES) != group_key(triangle, _KAMA_ALIASES)


def test_group_key_kama_brand_same_group() -> None:
    with_brand = _row(manufacturer_name="НКШЗ", brand="Кама", model="NU701")
    without = _row(manufacturer_name="НКШЗ", model="NU701")
    assert group_key(with_brand, _KAMA_ALIASES) == group_key(without, _KAMA_ALIASES)


def test_group_key_list_alias_uses_key() -> None:
    assert "aeolus" in group_key(_row(manufacturer_name="Aeolus"), {"Aeolus": ["Аеолус"]})


def test_group_key_keeps_non_numeric_diameter() -> None:
    assert "R16" in group_key(_row(diameter="R16"))


def test_group_key_comma_diameter_matches_dot() -> None:
    assert group_key(_row(diameter="22,5")) == group_key(_row(diameter="22.5"))


def test_group_key_inch_outer_diameter_from_title() -> None:
    item_35 = _row(title="35X12.50R17 Maxxis Trepador", model="Trepador", width="12.50", diameter="17")
    item_33 = _row(title="33X12.50R17 Maxxis Trepador", model="Trepador", width="12.50", diameter="17")
    assert group_key(item_35) != group_key(item_33)


def test_group_key_inch_lt_suffix_and_ext_field() -> None:
    from_title = _row(title="35x12.50R17LT Maxxis", model="Trepador", width="", diameter="")
    from_field = _row(title="Maxxis Trepador", model="Trepador", width="12.5", diameter="17", ext_diameter=35)
    assert group_key(from_title) == group_key(from_field)


def test_group_key_ignores_season_and_spike() -> None:
    filled = _row(season="Зимняя", spike="Да")
    blank = _row()
    assert group_key(filled) == group_key(blank)


def test_group_key_ignores_optional_disk_fields() -> None:
    blank = _row(type_production="диск", model="Rebel")
    filled = _row(
        type_production="диск",
        model="Rebel",
        slot_count=5,
        pcd1=114.3,
        eet=40,
        central_diameter=66.6,
        color="BKF",
    )
    assert group_key(blank) == group_key(filled)


def test_group_key_disk_thickness_splits() -> None:
    thin = _row(type_production="диск", disk_thickness="13.5", model="SRW")
    thick = _row(type_production="диск", disk_thickness="15,5", model="SRW")
    assert group_key(thin) != group_key(thick)


def test_group_key_run_flat_splits() -> None:
    plain = _row(model="Scorpion Verde All-Season")
    runflat = _row(model="Scorpion Verde All-Season", run_flat="Да")
    assert group_key(plain) != group_key(runflat)


def test_group_key_sidewall_splits() -> None:
    mud = _row(model="TRD06", inscription_on_the_side="M+S")
    winter = _row(model="TRD06", inscription_on_the_side="3PMSF")
    assert group_key(mud) != group_key(winter)


def test_group_key_tt_only_tire_splits_from_tt() -> None:
    tube = _row(camera_type="TT", title="no marker")
    tire_only = _row(camera_type="TT (только шина)", title="no marker")
    assert group_key(tube) != group_key(tire_only)


def test_group_key_camera_ttf_splits_from_tt() -> None:
    ttf = _row(camera_type="TTF", title="no marker")
    tube = _row(camera_type="TT", title="no marker")
    assert group_key(ttf) != group_key(tube)


_ZEPP_TITLE = "9.0x22.5 10x335 ET175 281 Sil Zepp 10/335/281/175 (16 мм) б/к"


def _zepp_disk(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "type_production": "диск",
        "model": "10/335/281/175",
        "width": "9.0",
        "diameter": "22.5",
        "manufacturer_name": "ZEPP",
        "disk_thickness": "16",
        "title": _ZEPP_TITLE,
    }
    payload.update(fields)
    return _row(**payload)


def test_group_key_disk_factory_splits() -> None:
    yz = _zepp_disk(title="{0} (YZ)".format(_ZEPP_TITLE))
    hap = _zepp_disk(title="{0} (HAP)".format(_ZEPP_TITLE))
    assert group_key(yz) != group_key(hap)


def test_group_key_disk_valve_splits() -> None:
    outer = _zepp_disk(title="{0} (HAP) alive наруж. вентиль".format(_ZEPP_TITLE))
    inner = _zepp_disk(title="{0} (HAP) внутр. вентиль".format(_ZEPP_TITLE))
    assert group_key(outer) != group_key(inner)


def test_group_key_same_disk_extras_match() -> None:
    first = _zepp_disk(title="{0} (YZ)".format(_ZEPP_TITLE))
    second = _zepp_disk(title="{0} (YZ)".format(_ZEPP_TITLE))
    assert group_key(first) == group_key(second)


def test_group_key_ignores_numeric_disk_code() -> None:
    coded = _zepp_disk(title="{0} (HAP) (5221105)".format(_ZEPP_TITLE))
    plain = _zepp_disk(title="{0} (HAP)".format(_ZEPP_TITLE))
    assert group_key(coded) == group_key(plain)


def test_group_key_passenger_disk_without_extras() -> None:
    with_model_code = _row(
        type_production="диск",
        model="Ягуар (КЛ147)",
        manufacturer_name="СКАД",
        width="5.5",
        diameter="14",
        title="5.5x14 4x98 ET38 58.6 Алмаз Скад Ягуар (КЛ147)",
    )
    same_model = _row(
        type_production="диск",
        model="Ягуар (КЛ147)",
        manufacturer_name="СКАД",
        width="5.5",
        diameter="14",
        title="5.5x14 Скад Ягуар (КЛ147)",
    )
    assert group_key(with_model_code) == group_key(same_model)
