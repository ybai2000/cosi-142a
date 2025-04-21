from enum import Enum
import threading

class App():
    class Button(Enum):
        SELECT = 1
        BACK = 2
        UP = 3
        DOWN = 4
    interrupt: int = 0
    
