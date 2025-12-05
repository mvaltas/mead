from __future__ import annotations
import contextvars
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from mead.model import Model

# Context variable to hold the currently active Model instance.
# Elements will check this variable upon initialization to auto-register.
current_model: contextvars.ContextVar[Optional[Model]] = contextvars.ContextVar(
    "current_model", default=None
)
