import string
from itertools import chain


class InvalidJSON(ValueError):
    pass


class UnexpectedSymbol(InvalidJSON):
    def __init__(self, symbol):
        self.symbol = symbol
        self.message = f'Unexpected symbol "{symbol}"'
        super().__init__(self.message)


DIGITS = string.digits + "-"
VALUE = '{["tfn' + DIGITS
VALUE_OR_ARRAY_AND = VALUE + "]"
KEY = '"'
KEY_OR_OBJECT_END = KEY + "}"
COMMA = ","
COMMA_OR_ARRAY_END = COMMA + "]"
COMMA_OR_OBJECT_END = COMMA + "}"
COLON = ":"


class JSONParser:
    def __init__(self):
        self.iterator = None

    def _push_back(self, symbol):
        self.iterator = chain([symbol], self.iterator)

    def _skip_whitespace(self, expected_symbols):
        while symbol := next(self.iterator):
            if symbol in string.whitespace:
                continue

            if symbol in expected_symbols:
                return symbol

            raise UnexpectedSymbol(symbol)

    def _parse_value(self):
        symbol = self._skip_whitespace(VALUE)
        if symbol == "{":
            return self._parse_object()
        if symbol == "[":
            return self._parse_array()
        if symbol == '"':
            return self._parse_string()
        if symbol in DIGITS:
            self._push_back(symbol)
            return self._parse_number()
        if symbol in "tfn":
            self._push_back(symbol)
            return self._parse_literal()

    def _parse_string(self):
        letters = []
        while symbol := next(self.iterator):
            if symbol == '"':
                break
            letters.append(symbol)
        return "".join(letters)

    def _parse_literal(self):
        literals = {
            "t": ("rue", True),
            "f": ("alse", False),
            "n": ("ull", None),
        }

        first_symbol = next(self.iterator)

        remaining, value = literals[first_symbol]

        while remaining and (symbol := next(self.iterator)):
            if symbol != remaining[0]:
                raise UnexpectedSymbol(symbol)

            remaining = remaining[1:]

        return value

    def _parse_number(self):
        digits = []
        while symbol := next(self.iterator, None):
            if symbol not in DIGITS + ".":
                self._push_back(symbol)
                break
            digits.append(symbol)
        digits = "".join(digits)
        if "." in digits:
            return float(digits)
        return int(digits)

    def _parse_array(self):
        array = []
        next_expecting = {
            VALUE_OR_ARRAY_AND: COMMA_OR_ARRAY_END,
            COMMA_OR_ARRAY_END: VALUE,
            VALUE: COMMA_OR_ARRAY_END,
        }

        expecting = VALUE_OR_ARRAY_AND
        while True:
            symbol = self._skip_whitespace(expecting)

            if symbol == "]":
                return array

            if expecting in {VALUE_OR_ARRAY_AND, VALUE}:
                self._push_back(symbol)
                array.append(self._parse_value())

            expecting = next_expecting[expecting]

    def _parse_object(self):
        obj = {}
        next_expecting = {
            KEY_OR_OBJECT_END: COLON,
            COLON: VALUE,
            VALUE: COMMA_OR_OBJECT_END,
            COMMA_OR_OBJECT_END: KEY,
            KEY: COLON,
        }

        expecting = KEY_OR_OBJECT_END
        current_key = None
        while True:
            symbol = self._skip_whitespace(expecting)

            if symbol == "}":
                return obj

            if expecting in {KEY, KEY_OR_OBJECT_END}:
                current_key = self._parse_string()
            elif expecting == VALUE:
                self._push_back(symbol)
                obj[current_key] = self._parse_value()

            expecting = next_expecting[expecting]

    def loads(self, text: str):
        self.iterator = text.__iter__()

        try:
            value = self._parse_value()
        except StopIteration:
            raise InvalidJSON()

        # This ensures that we only have whitespace after the value, and not anything else
        try:
            self._skip_whitespace(expected_symbols=[])
        except StopIteration:
            pass
        else:
            raise InvalidJSON()

        return value



json = JSONParser()


__all__ = ["json", "InvalidJSON", "UnexpectedSymbol"]
