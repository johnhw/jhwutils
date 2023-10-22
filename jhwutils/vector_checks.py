import ast, inspect
from textwrap import dedent

## From https://stackoverflow.com/questions/36662181/is-there-a-way-to-check-if-function-is-recursive-in-python
from bdb import Bdb
import sys
import numpy as np


class RecursionDetected(Exception):
    pass


class RecursionDetector(Bdb):
    def do_clear(self, arg):
        pass

    def __init__(self, *args):
        Bdb.__init__(self, *args)
        self.stack = set()

    def user_call(self, frame, argument_list):
        code = frame.f_code
        if code in self.stack:
            raise RecursionDetected
        self.stack.add(code)

    def user_return(self, frame, return_value):
        self.stack.remove(frame.f_code)


def test_recursion(func):
    detector = RecursionDetector()
    detector.set_trace()
    try:
        func()
    except RecursionDetected:
        return True
    else:
        return False
    finally:
        sys.settrace(None)


def check_ast(fn, forbidden_nodes=None, required_nodes=None, required_names=None, forbidden_names=None):
    required_nodes = required_nodes or []
    forbidden_nodes = forbidden_nodes or []
    required_names = required_names or []
    forbidden_names = forbidden_names or []
    tree = ast.parse(dedent(inspect.getsource(fn)))
    required_nodes = set(required_nodes)
    required_names = set(required_names)
    for node in ast.walk(tree):                
        name = None 
        if type(node)==ast.Name:
            name = node.id 
        if type(node)==ast.Attribute:
            name = node.attr 
        if name is not None:
            if name in forbidden_names:
                return False
            if name in required_names:
                required_names.remove(name)            
        if type(node) in forbidden_nodes:
            return False
        if type(node) in required_nodes:
            required_nodes.remove(type(node))
    if len(required_nodes) > 0 or len(required_names)>0:
        return False
    else:
        return True



def check_vectorised(fn):
    tree = ast.parse(dedent(inspect.getsource(fn)))
    for node in ast.walk(tree):
        if type(node) == ast.For:
            print("Hey, you used 'for'!")
            return False
        if type(node) == ast.ListComp:
            print("No list comprehensions, champ.")
            return False
        if type(node) == ast.DictComp:
            print("I know about dictionary comprehensions, too. No go.")
            return False
        if type(node) == ast.SetComp:
            print("Set comprehensions? Really?")
            return False
        if type(node) == ast.comprehension:
            print("Good try, but that's still iteration")
            return False
        if type(node) == ast.While:
            print("No 'while' loops, buddy.")
            return False
    return True


def check_is_vectorised(f, vec_f, *args, **kwargs):
    if not check_vectorised(vec_f):
        print("Not a vectorised function. Use NumPy.")
        return False
    # recursion = test_recursion(lambda :vec_f(*args, **kwargs))
    # if recursion:
    #     print("Recursion won't fool me.")
    #     return False
    expected = f(*args, **kwargs)
    actual = vec_f(*args, **kwargs)

    if not np.allclose(expected, actual):
        print("Values don't match")
        return False
    return True


if __name__ == "__main__":
    import numpy as np

    def f(x):
        a = []
        for i in range(x):
            a.append(i)
        for i in range(x):
            a[i] = a[i] * x
        return np.array(a)

    def while_f(x):
        a = []
        i = 0
        while i < x:
            a.append(i)
            i += 1
        for i in range(x):
            a[i] = a[i] * x
        return np.array(a)

    def lc_f(x):
        return np.array([i * x for i in range(x)])

    def vec_f(x):
        return np.arange(x) * x

    assert check_is_vectorised(f, vec_f, 10)  # OK
    assert not check_is_vectorised(f, f, 10)  # for
    assert not check_is_vectorised(f, while_f, 10)  # for
    assert not check_is_vectorised(f, lc_f, 10)  # for
