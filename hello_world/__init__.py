print("Initializing hello world module")
from .some_funcs import say_hello, repeat_string, create_dict

__all__ = ["say_hello", "repeat_string", "create_dict"]
