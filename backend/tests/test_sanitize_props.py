from src.tools.graph import _sanitize_props


def test_sanitize_props_drops_non_primitives():
    props = {
        "ok_str": "yes",
        "ok_int": 3,
        "ok_list": ["a", 2, True],
        "nested_dict": {"foo": "bar"},
        "mixed_list": ["keep", {"drop": "me"}, 5],
        "none_val": None,
    }

    cleaned = _sanitize_props(props)

    assert cleaned["ok_str"] == "yes"
    assert cleaned["ok_int"] == 3
    assert cleaned["ok_list"] == ["a", 2, True]
    # nested dict removed
    assert "nested_dict" not in cleaned
    # mixed list keeps only primitives
    assert cleaned["mixed_list"] == ["keep", 5]
    # None dropped
    assert "none_val" not in cleaned
