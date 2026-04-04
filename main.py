from z3 import *

if __name__ == "__main__":
    x = Int('x')
    s = Solver()
    s.add(x > 5)
    print(s.check())
    print(s.model())