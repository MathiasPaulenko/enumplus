from __future__ import annotations

import pytest

from enumplus import Enum


class TestCaseInsensitive:
    def test_from_value_case_insensitive(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        assert Color.from_value("Red", case_insensitive=True) is Color.RED
        assert Color.from_value("GREEN", case_insensitive=True) is Color.GREEN
        assert Color.from_value("rEd", case_insensitive=True) is Color.RED

    def test_from_value_case_insensitive_not_found(self) -> None:
        class Color(Enum):
            RED = "red"

        try:
            Color.from_value("blue", case_insensitive=True)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_from_value_case_insensitive_with_default(self) -> None:
        class Color(Enum):
            RED = "red"

        assert Color.from_value("Blue", case_insensitive=True, default=None) is None

    def test_from_name_case_insensitive(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        assert Color.from_name("red", case_insensitive=True) is Color.RED
        assert Color.from_name("green", case_insensitive=True) is Color.GREEN
        assert Color.from_name("ReD", case_insensitive=True) is Color.RED

    def test_from_name_case_insensitive_not_found(self) -> None:
        class Color(Enum):
            RED = "red"

        try:
            Color.from_name("blue", case_insensitive=True)
            raise AssertionError("Should have raised KeyError")
        except KeyError:
            pass

    def test_from_value_case_insensitive_non_string(self) -> None:
        class Number(Enum):
            ONE = 1
            TWO = 2

        assert Number.from_value(1, case_insensitive=True) is Number.ONE
        assert Number.from_value(2, case_insensitive=True) is Number.TWO


class TestToDict:
    def test_to_dict_basic(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        d = Color.to_dict()
        assert "RED" in d
        assert d["RED"]["value"] == "red"
        assert d["RED"]["label"] == "Red"
        assert d["RED"]["metadata"] == {}
        assert d["GREEN"]["value"] == "green"
        assert d["GREEN"]["label"] == "Green"

    def test_to_dict_with_metadata(self) -> None:
        class Color(Enum):
            RED = ("red", {"hex": "#FF0000"})
            GREEN = "green"

        d = Color.to_dict()
        assert d["RED"]["metadata"] == {"hex": "#FF0000"}
        assert d["RED"]["label"] == "Red"
        assert d["GREEN"]["metadata"] == {}

    def test_to_dict_with_custom_label(self) -> None:
        class Status(Enum):
            IN_PROGRESS = ("in_progress", {"label": "In Progress"})

        d = Status.to_dict()
        assert d["IN_PROGRESS"]["label"] == "In Progress"


class TestGet:
    def test_get_returns_member(self) -> None:
        class Color(Enum):
            RED = "red"

        assert Color.get("red") is Color.RED

    def test_get_returns_default(self) -> None:
        class Color(Enum):
            RED = "red"

        assert Color.get("blue", default=None) is None
        assert Color.get("blue", default=Color.RED) is Color.RED

    def test_get_default_is_none(self) -> None:
        class Color(Enum):
            RED = "red"

        assert Color.get("blue") is None


class TestGetInitial:
    def test_get_initial(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        assert Color.get_initial() is Color.RED

    def test_get_initial_single_member(self) -> None:
        class Single(Enum):
            ONLY = 1

        assert Single.get_initial() is Single.ONLY

    def test_get_initial_empty_raises(self) -> None:
        class Empty(Enum):
            pass

        try:
            Empty.get_initial()
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass


class TestGetFinal:
    def test_get_final(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        assert Color.get_final() is Color.BLUE

    def test_get_final_single_member(self) -> None:
        class Single(Enum):
            ONLY = 1

        assert Single.get_final() is Single.ONLY

    def test_get_final_empty_raises(self) -> None:
        class Empty(Enum):
            pass

        try:
            Empty.get_final()
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass


class TestKeys:
    def test_keys_returns_names(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        assert Color.keys() == ["RED", "GREEN"]

    def test_keys_empty(self) -> None:
        class Empty(Enum):
            pass

        assert Empty.keys() == []

    def test_keys_equals_names(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        assert Color.keys() == Color.names()


class TestMap:
    def test_map_basic(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        result = Color.map({Color.RED: "#FF0000", Color.GREEN: "#00FF00"})
        assert result == {"RED": "#FF0000", "GREEN": "#00FF00"}

    def test_map_partial(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        result = Color.map({Color.RED: "#FF0000"})
        assert result == {"RED": "#FF0000", "GREEN": None}

    def test_map_empty(self) -> None:
        class Color(Enum):
            RED = "red"

        result = Color.map({})
        assert result == {"RED": None}


class TestI18nLabels:
    def test_callable_label(self) -> None:
        translations = {"RED": "Rojo", "GREEN": "Verde"}

        def translate(key: str) -> str:
            return translations.get(key, key)

        class Color(Enum):
            RED = ("red", {"label": lambda: translate("RED")})
            GREEN = ("green", {"label": lambda: translate("GREEN")})

        assert Color.RED.label == "Rojo"
        assert Color.GREEN.label == "Verde"

    def test_callable_label_changes_with_locale(self) -> None:
        current_locale: dict[str, str] = {"lang": "en"}
        en = {"RED": "Red", "GREEN": "Green"}
        es = {"RED": "Rojo", "GREEN": "Verde"}

        def translate(key: str) -> str:
            lang = current_locale["lang"]
            table = es if lang == "es" else en
            return table.get(key, key)

        class Color(Enum):
            RED = ("red", {"label": lambda: translate("RED")})
            GREEN = ("green", {"label": lambda: translate("GREEN")})

        assert Color.RED.label == "Red"
        current_locale["lang"] = "es"
        assert Color.RED.label == "Rojo"
        assert Color.GREEN.label == "Verde"
        current_locale["lang"] = "en"
        assert Color.RED.label == "Red"

    def test_non_callable_label_unchanged(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": "Red"})

        assert Color.RED.label == "Red"

    def test_callable_label_in_choices(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": lambda: "Rojo"})

        assert Color.choices() == [("red", "Rojo")]

    def test_callable_label_in_to_dict(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": lambda: "Rojo"})

        d = Color.to_dict()
        assert d["RED"]["label"] == "Rojo"

    def test_callable_label_in_str(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": lambda: "Rojo"})

        assert str(Color.RED) == "Rojo"

    def test_callable_label_in_labels(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": lambda: "Rojo"})
            GREEN = ("green", {"label": lambda: "Verde"})

        assert Color.labels() == ["Rojo", "Verde"]

    def test_callable_label_in_to_json(self) -> None:
        class Color(Enum):
            RED = ("red", {"label": lambda: "Rojo"})

        import json

        data = json.loads(Color.to_json())
        assert data["members"][0]["label"] == "Rojo"

    def test_non_label_callable_not_invoked_in_to_dict(self) -> None:
        def callback() -> str:
            return "called"

        class Color(Enum):
            RED = ("red", {"label": "Red", "callback": callback})

        d = Color.to_dict()
        assert d["RED"]["label"] == "Red"
        assert callable(d["RED"]["metadata"]["callback"])
        assert d["RED"]["metadata"]["callback"] is callback

    def test_non_label_callable_not_invoked_in_to_json(self) -> None:
        def callback() -> str:
            return "called"

        class Color(Enum):
            RED = ("red", {"label": "Red", "callback": callback})

        with pytest.raises(TypeError):
            Color.to_json()


class TestSerializeByName:
    def test_flag_default_false(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

        assert Color.serialize_by_name is False

    def test_flag_set_true(self) -> None:
        class Color(Enum):
            RED = "red"
            GREEN = "green"

            serialize_by_name = True

        assert Color.serialize_by_name is True

    def test_flag_inherited_from_empty_base(self) -> None:
        class Base(Enum):
            serialize_by_name = True

        class Child(Base):  # type: ignore[misc]
            A = 1
            B = 2

        assert Child.serialize_by_name is True

    def test_flag_override_in_subclass(self) -> None:
        class Base(Enum):
            serialize_by_name = True

        class Child(Base):  # type: ignore[misc]
            serialize_by_name = False  # type: ignore[misc]
            A = 1

        assert Child.serialize_by_name is False

    def test_flag_not_inherited_without_base(self) -> None:
        class Base(Enum):
            serialize_by_name = True

        class Sibling(Enum):
            A = 1

        assert Sibling.serialize_by_name is False
