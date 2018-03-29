from ..ns import qn
from ..simpletypes import ST_BrClear, ST_BrType
from ..xmlchemy import (
    BaseOxmlElement, OptionalAttribute, ZeroOrMore, ZeroOrOne
)

class CT_Comment(BaseOxmlElement):
    def __init__(self):
        print("do a comment")