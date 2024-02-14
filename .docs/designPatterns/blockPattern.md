# Block Pattern

Usually, when doing initial design, we divide our code into many blocks. These blocks contain functionality, and exchange information with each other.

In this example, we'll discuss how to structure code for two blocks, one called `SenderBlock` and the other called `RecieverBlock`. These names are just for example.

```
    ------------------                        ------------------
    |                |                        |                |  
    |  SenderBlock   | ---------------------> | RecieverBlock  |  
    |                |         someVal        |                |
    ------------------                        ------------------
```

## Blocks

Generally, we will create a new python file and a new class for each block. For example:

**`senderBlock.py`**
```py
class SenderBlock():
    # ...

```

**`recieverBlock.py`**
```py
class RecieverBlock():
    # ...
    
```

Remember that classes are simply patterns for how to create functionalty. To actually invoke their functionality, you have to _instantiate_ an _object_ with the class as its type.

In our case, we will need to create one of each block in `robot.py`. Note that we must import class definitions before using them.

**`robot.py`**
```py
import wpilib
from senderBlock import SenderBlock
from recieverBlock import RecieverBlock

class MyRobot(wpilib.TimedRobot):

    def robotInit(self): 
        self.s = SenderBlock()
        self.r = RecieverBlock()
```

## Init/Update

First, each block is assumed to contain at least two types of code.

Some code is for _initilization_ - it has to be run once, to perform one-time setup steps.

Init code should generally go in the _constructor_ of the class for the block.

Some code is for _periodic_ execution - it has to run in every 20ms loop to read inputs, perform calculation, and supply new outputs.

Periodic execution is, by convention, usually put in a function called `update()`.

**`senderBlock.py`**
```py
class SenderBlock():
    def __init__(self):
        # Put all init code here

    def update(self):
        # Put all periodic code here

```

**`recieverBlock.py`**
```py
class RecieverBlock():
    def __init__(self):
        # Put all init code here

    def update(self):
        # Put all periodic code here
    
```

Once the functions have been created, it's import to remember they have to be called. Again, we'll do this in `robot.py`:


**`robot.py`**
```py
import wpilib
from senderBlock import SenderBlock
from recieverBlock import RecieverBlock

class MyRobot(wpilib.TimedRobot):

    def robotInit(self): 
        self.s = SenderBlock()
        self.r = RecieverBlock()

    def robotPeriodic(self):
        self.s.update()
        self.r.update()
```


## Set/Get

We see one piece of data, `someVal`, is transferred between the blocks.

`someVal` is an _output_ of `SenderBlock`. `someVal` is an _input_ of `RecieverBlock`.

**`senderBlock.py`**
```py
class SenderBlock():
    def __init__(self):
        # Put all init code here
        self.someValue = 0  #pick a default value

    def update(self):
        # Put all periodic code here

    def getSomeValue(self):
        return self.someValue 

```

**`recieverBlock.py`**
```py
class RecieverBlock():
    def __init__(self):
        # Put all init code here
        self.someValue = 0 #pick a default value

    def update(self):
        # Put all periodic code here

    def setSomeValue(self, valIn):
        self.someValue = valIn
```

Finally, in `robot.py`, hook the setter and getter to each other:

**`robot.py`**
```py
import wpilib
from senderBlock import SenderBlock
from recieverBlock import RecieverBlock

class MyRobot(wpilib.TimedRobot):

    def robotInit(self): 
        self.s = SenderBlock()
        self.r = RecieverBlock()

    def robotPeriodic(self):
        self.s.update()

        tmp = self.s.getSomeValue()
        self.r.setSomeValue(tmp)

        self.r.update()
```

We have now fully implemented a two-block architecture with init, update, and passing one piece of data.

## Singletons

So far, we've assumed objects for the blocks were created in the same class (`MyRobot` in `robot.py`), and the action of passing data between them is done in that class.

Making one or more of the blocks singletons enables more flexibility on where the data is passed between blocks.

### Singelton Sender Example

When the sender is a singleton, the data should get passed in the update method of the reciever. A setter method is not needed.

**`senderBlock.py`**
```py
from utils.singleton import Singleton

class SenderBlock(metaclass=Singleton):
    def __init__(self):
        # Put all init code here
        self.someValue = 0  #pick a default value

    def update(self):
        # Put all periodic code here

    def getSomeValue(self):
        return self.someValue 

```

**`recieverBlock.py`**
```py

from senderBlock import SenderBlock

class RecieverBlock():
    def __init__(self):
        # Put all init code here
        self.someValue = 0 #pick a default value

    def update(self):
        self.someValue = SenderBlock().getSomeValue()
        # Put additional calculation here
```

Finally, in `robot.py`, we now only need to do updates.

**`robot.py`**
```py
import wpilib
from senderBlock import SenderBlock
from recieverBlock import RecieverBlock

class MyRobot(wpilib.TimedRobot):

    def robotInit(self): 
        self.r = RecieverBlock()

    def robotPeriodic(self):
        SenderBlock.update()
        self.r.update()
```
