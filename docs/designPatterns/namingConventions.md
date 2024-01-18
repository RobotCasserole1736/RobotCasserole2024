# Naming Conventions

For naming things consistently, we enforce the following conventions for how to create the names of variables, classes, and files.

## Names

In general, names should be descriptive. Unlike in math, single letter variable names are not recommended.

Pick a set of words which describes your meaning. 

Order your words from general to specific. For example:

```py
drivetrainModuleFrontLeftWheelEncoderFaulted = False
```

* Drivetrain is the "biggest" thing
* Module is one of four in a Drivetrain
* Front-Left specifies whcih of the four modules we're talking about
* Encoder is one part of that module
* Faulted describes one part of the state of the Encoder.

Use as many words as you need to, but avoid being redundant. For example:

```py
class Drivetrain():
    # ...
    def update(self):
        # ...
        # Bad name - "drivetrain" is redundant, because this is already a member of the "drivetrain" class
        self.drivetrainModuleFrontLeftWheelEncoderFaulted = False

        # Better name
        self.moduleFrontLeftWheelEncoderFaulted = False
```

## Cases

The "casing" of a name refers to which letters get capitalized and which letters are lowercase.

### Snake Case

Snake Case uses all lower case letters, and separates words with underscores

`my_variable_name`

### Screaming Snake Case

Same as Snake Case, but uses all upper case letters

`MY_VARIABLE_NAME`

### Camel Case

Camel Case attaches all words together without underscores, and capatilizes the first letter of each word, except for the first word.

`myVariableName`

### Pascal Case

Same as Camel Case, but with the first word also capitalized like the rest:

`MyVariableName`

## Case Usage

While python does not require using any particular case, for consistency, we choose the following convention:

* `snake_case`
  * Not Used
* `SCREAMING_SNAKE_CASE`
  * Constant numeric values which will never change
* `camelCase`
  * Python `.py` file names
  * All Variable, funciton, and method names
* `PascalCase`
  * Class names