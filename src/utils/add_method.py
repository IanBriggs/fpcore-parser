#   __   ____  ____        _  _  ____  ____  _  _   __  ____     ____  _  _
#  / _\ (    \(    \      ( \/ )(  __)(_  _)/ )( \ /  \(    \   (  _ \( \/ )
# /    \ ) D ( ) D ( ____ / \/ \ ) _)   )(  ) __ ((  O )) D ( _  ) __/ )  /
# \_/\_/(____/(____/(____)\_)(_/(____) (__) \_)(_/ \__/(____/(_)(__)  (__/
#
# A decorator which allows class methods to be put in a different file
#

def add_method(aClass):
    """Attaches the decorated function to the defined class"""
    def inner(func):
        setattr(aClass, func.__name__, func)
        return func
    return inner
