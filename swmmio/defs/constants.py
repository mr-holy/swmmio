from dataclasses import dataclass

@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    def as_tuple(self): return (self.r, self.g, self.b)

RED = Color(250, 5, 5)
BLUE = Color(5, 5, 250)
# etc...
