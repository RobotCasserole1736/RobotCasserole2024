# Singletons

In code, we frequently want to indicate "there is only ever one of these". The Singleton pattern sets up a class for which there is only ever one instance, which can be accessed everywhere.

## Metaclass

Python supports the concept of "metaclass", which alters the way classes are constructed.

An implementation of a singleton metaclass in `utils.singleton`.

## Making a Singleton

Declare your class like normal. In addition, import the singleton metaclass:

```py
from utils.singleton import Singleton
```

Then, change your classes metaclass:

```py
class MyNewSingletonClass(metaclass=Singleton):
    # Rest of the class looks normal, except...
    def __init__(self):
        # the constructor cannot take argumets other than `self`
```

## Using a Singleton

Import the class like normal:

```py
from folder.filename import MyNewSingletonClass
```

Then, whenever you need to access the single instance of the class, invoke its name follwed by `()`:

```py
MyNewSingletonClass().someMethod()
```


## Handling clean shutdown

For proper unit testing, our robot needs to fully destroy all usages of hardware resources. If any of these happen in a singleton, the teardown only happens when the class is "disposed of". 

We keep track of all of our singleton instances in a dictionary, and provide an API which can be called to destroy them all.

This should only be called on the destruction of the main robot class.

```py
from utils.singleton import destroyAllSingletonInstances

# ...

class MyRobot(wpilib.TimedRobot):
    # ...
    def endCompetition(self):
        destroyAllSingletonInstances()
```

