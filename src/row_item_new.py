# Source - https://stackoverflow.com/a
# Posted by Chris May, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-03, License - CC BY-SA 4.0

from dataclasses import dataclass, field


class Descriptor:
    def __init__(self, default):
        self.default = default

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if value is self:
            value = self.default
        else:
            value = int(value)
        setattr(obj, self.private_name, value)


@dataclass
class Person:
    age: str = field(default=Descriptor(default=3))


if __name__ == "__main__":
    r = Person(2.37)
    assert r.age == 2
    p = Person()
    assert p.age == 3
    print(r)
    print(p)
    print(vars(p))
