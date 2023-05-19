from .constants import *

class SanityChecker():
    
    def __init__(self):
        self.clean() 

    def clean(self):
        self.positions = []

    def checkPositionIsFree(self, position):
        if not position in self.positions:
            return True
        else:
            return False