from .components import Element
from typing import TypeVar, Generic

T = TypeVar("T", bound="Element")


class InspectConfig:
    def __init__(self):
        self.show_attrs = set()
        self.hide_attrs = set()
        self.show_all = False
        self.hide_all = False

    def show(self, *names):
        self.show_attrs.update(names)

    def hide(self, *names):
        self.hide_attrs.update(names)


class InspectMeta(type):
    def __instancecheck__(cls, obj):
        if isinstance(obj, Inspect):
            return isinstance(obj._element, cls)
        return super().__instancecheck__(obj)


class Inspect(Generic[T], metaclass=InspectMeta):
    config = InspectConfig()

    def __init__(self, element: T):
        self._element = element

    @property
    def __class__(self):
        return self._element.__class__

    def __repr__(self) -> str:
        return self._render()

    def __str__(self) -> str:
        return self._render()

    def __call__(self) -> T:
        return self._element

    def __getattr__(self, name):
        attr = getattr(self._element, name)

        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if self._should_show(name):
                    print(f"{self!r}: {name}({args}, {kwargs}) -> {result}")
                return result

            return wrapper
        return attr

    def _render(self):
        attrs = vars(self._element)
        out = []
        for name, value in attrs.items():
            if self._should_show(name):
                out.append(f"{name}={value!r}")

        return f"<Inspect of {self._element.__class__.__name__}({', '.join(out)})>"

    def _should_show(self, name):
        cfg = self.config

        if cfg.show_all:
            return name not in cfg.hide_attrs
        if cfg.hide_all:
            return name in cfg.show_attrs
        if name in cfg.hide_attrs:
            return False
        if name in cfg.show_attrs:
            return True
        return True
