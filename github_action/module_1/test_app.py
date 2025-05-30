from app import add, greet

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_greet():
    assert greet("Alice") == "Hello, Alice!"
