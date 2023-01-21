import pytest

from parser import parser, InvalidJSON


def check_example(source, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            parser.parse(source)
    else:
        assert parser.parse(source) == expected


@pytest.mark.parametrize(
    "source, expected",
    [
        ("8", 8),
        ("-42", -42),
        ("0x42", InvalidJSON),
    ],
)
def test_number(source, expected):
    check_example(source, expected)


@pytest.mark.parametrize(
    "source, expected",
    [
        ('"qwerty"', "qwerty"),
        ('""', ""),
        ('"a/*b*/c/*d//e"', "a/*b*/c/*d//e"),
        ("", InvalidJSON),
    ],
)
def test_string(source, expected):
    check_example(source, expected)


@pytest.mark.parametrize(
    "source, expected",
    [
        ('["qwerty", "asd", 0]', ["qwerty", "asd", 0]),
        (
            '["foo", 1, true, false, null, {"bar": 0}]',
            ["foo", 1, True, False, None, {"bar": 0}],
        ),
        ("[[[[]]]]", [[[[]]]]),
        ("[[],[[]]]", [[], [[]]]),
        ("]", InvalidJSON),
        ("[[]]]", InvalidJSON),
        ("[,1]", InvalidJSON),
        ('[" ": 1]', InvalidJSON),
        ("[1,\n1\n,1", InvalidJSON),
    ],
)
def test_array(source, expected):
    check_example(source, expected)


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            '{"qwerty": "asd", "foo": ["bar1", "bar2"]}',
            {"qwerty": "asd", "foo": ["bar1", "bar2"]},
        ),
        (
            '{"qwerty": "asd", "foo": {"bar": "baz"}}',
            {"qwerty": "asd", "foo": {"bar": "baz"}},
        ),
        ('{"":0}', {"": 0}),
        ('{"a":"b","a":"b"}', {"a": "b"}),
        ("{1:1}", InvalidJSON),
        ('{:"b"}', InvalidJSON),
        ("{key: 'value'}", InvalidJSON),
        ("{key: 'value'}", InvalidJSON),
        ('{"x"::"b"}', InvalidJSON),
        ('{"id":0,}', InvalidJSON),
        ('{"id":0,,,,,}', InvalidJSON),
        ('{"":', InvalidJSON),
        ("{}}", InvalidJSON),
        ('{"a":"b"}/**/', InvalidJSON),
        ('{"a":/*comment*/"b"}', InvalidJSON),
    ],
)
def test_object(source, expected):
    check_example(source, expected)


@pytest.mark.parametrize(
    "source, expected",
    [
        ("null", None),
        ("n", InvalidJSON),
        ("none", InvalidJSON),
        ("Null", InvalidJSON),
        ("true", True),
        ("t", InvalidJSON),
        ("True", InvalidJSON),
        ("false", False),
        ("fa", InvalidJSON),
        ("False", InvalidJSON),
        ("something", InvalidJSON),
    ],
)
def test_literals(source, expected):
    check_example(source, expected)
