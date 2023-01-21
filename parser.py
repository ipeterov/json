import itertools
import string


class InvalidJSON(ValueError):
    pass


class UnexpectedSymbol(InvalidJSON):
    def __init__(self, symbol):
        self.symbol = symbol
        self.message = f'Unexpected symbol "{symbol}"'
        super().__init__(self.message)


VALUE = '{["tfn' + string.digits
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

    def parse(self, text: str):
        self.iterator = text.__iter__()

        try:
            value = self.value_handler()
        except StopIteration:
            raise InvalidJSON()

        try:
            self.skip_whitespace(expected_symbols=[])
        except StopIteration:
            pass
        else:
            raise InvalidJSON()

        return value

    def value_handler(self):
        symbol = self.skip_whitespace(VALUE)
        if symbol == "{":
            return self.object_handler()
        if symbol == "[":
            return self.array_handler()
        if symbol == '"':
            return self.string_handler()
        if symbol in string.digits:
            self.push_back(symbol)
            return self.number_handler()
        if symbol in "tfn":
            return self.literal_handler(symbol)

    def push_back(self, symbol):
        self.iterator = itertools.chain([symbol], self.iterator)

    def skip_whitespace(self, expected_symbols):
        while symbol := next(self.iterator):
            if symbol in string.whitespace:
                continue

            if symbol in expected_symbols:
                return symbol

            raise UnexpectedSymbol(symbol)

    def literal_handler(self, first_symbol):
        literals = {
            "t": ("rue", True),
            "f": ("alse", False),
            "n": ("ull", None),
        }

        remaining, value = literals[first_symbol]

        while remaining and (symbol := next(self.iterator)):
            if symbol != remaining[0]:
                raise UnexpectedSymbol(symbol)

            remaining = remaining[1:]

        return value

    def string_handler(self):
        letters = []
        while symbol := next(self.iterator):
            if symbol == '"':
                break
            letters.append(symbol)
        return "".join(letters)

    def number_handler(self):
        digits = []
        while symbol := next(self.iterator, None):
            if symbol not in string.digits + ".":
                self.push_back(symbol)
                break
            digits.append(symbol)
        digits = "".join(digits)
        if "." in digits:
            return float(digits)
        return int(digits)

    def array_handler(self):
        array = []
        next_expecting = {
            VALUE_OR_ARRAY_AND: COMMA_OR_ARRAY_END,
            COMMA_OR_ARRAY_END: VALUE,
            VALUE: COMMA_OR_ARRAY_END,
        }

        expecting = VALUE_OR_ARRAY_AND
        while True:
            symbol = self.skip_whitespace(expecting)

            if symbol == "]":
                return array

            if expecting in {VALUE_OR_ARRAY_AND, VALUE}:
                self.push_back(symbol)
                array.append(self.value_handler())

            expecting = next_expecting[expecting]

    def object_handler(self):
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
            symbol = self.skip_whitespace(expecting)

            if symbol == "}":
                return obj

            if expecting in {KEY, KEY_OR_OBJECT_END}:
                current_key = self.string_handler()
            elif expecting == VALUE:
                self.push_back(symbol)
                obj[current_key] = self.value_handler()

            expecting = next_expecting[expecting]


parser = JSONParser()
