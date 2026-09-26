from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer, WithJsonSchema

Money = Annotated[
    Decimal,
    PlainSerializer(lambda value: float(value), return_type=float, when_used="json"),
    WithJsonSchema({"type": "number", "format": "decimal"}),
]
