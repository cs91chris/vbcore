import re


class Case:
    REG_CHECK_CAMEL = re.compile(r"^([A-Z]).([0-9a-zA-Z])*$")
    REG_CHECK_DROME = re.compile(r"^([a-z]).([0-9a-zA-Z])*$")
    REG_CHECK_SNAKE = re.compile(r"((^|_+)[a-z0-9]*)*$")
    REG_CHECK_KEBAB = re.compile(r"((^|-+)[a-z0-9]*)*$")
    REG_CHECK_WORDS = re.compile(r"^([a-zA-Z]).([0-9a-zA-Z]*)\s+([0-9a-zA-Z\s]*)*$")
    REG_SUB_CAMEL = re.compile(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")

    @classmethod
    def is_camel(cls, text: str) -> bool:
        return bool(cls.REG_CHECK_CAMEL.match(text))

    @classmethod
    def is_drome(cls, text: str) -> bool:
        return bool(cls.REG_CHECK_DROME.match(text))

    @classmethod
    def is_snake(cls, text: str) -> bool:
        return bool(cls.REG_CHECK_SNAKE.match(text))

    @classmethod
    def is_kebab(cls, text: str) -> bool:
        return bool(cls.REG_CHECK_KEBAB.match(text))

    @classmethod
    def are_words(cls, text: str) -> bool:
        return bool(cls.REG_CHECK_WORDS.match(text))

    @classmethod
    def to_drome(cls, text: str) -> str:
        def first_case(t: str) -> str:
            return t[0].lower() + t[1:]

        if cls.is_drome(text):
            return text
        if cls.is_camel(text):
            return first_case(text)

        return first_case("".join(w for w in text.title() if w.isalnum()))

    @classmethod
    def to_camel(cls, text: str) -> str:
        def first_case(t: str) -> str:
            return t[0].upper() + t[1:]

        if cls.is_camel(text):
            return text
        if cls.is_drome(text):
            return first_case(text)

        return first_case("".join(w for w in text.title() if w.isalnum()))

    @classmethod
    def to_snake(cls, text: str) -> str:
        return cls.REG_SUB_CAMEL.sub(r"_\1", cls.to_camel(text)).lower()

    @classmethod
    def to_kebab(cls, text: str) -> str:
        return cls.REG_SUB_CAMEL.sub(r"-\1", cls.to_camel(text)).lower()

    @classmethod
    def to_words(cls, text: str) -> str:
        if cls.is_camel(text) or cls.is_drome(text):
            return cls.REG_SUB_CAMEL.sub(r" \1", text)
        return "".join(w if w.isalnum() else " " for w in text)
