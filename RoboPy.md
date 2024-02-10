# firstRoboPy
A very simple first attempt at robot written in python

![Workflow Status](https://github.com/RobotCasserole1736/firstRoboPy/actions/workflows/ci.yml/badge.svg)

## Installation

Before developing code on a new computer, perform the following:

1. [Download and install wpilib](https://github.com/wpilibsuite/allwpilib/releases)
2. [Download and install python](https://www.python.org/downloads/)
3. Run these commands:

```cmd
    python -m pip install --upgrade pip
    python -m pip install -r requirements_dev.txt
    python -m pip install robotpy
    robotpy sync
```

## Docs

[Click here to see documentation for common libraries](docs/UserAPI).

## Deploying to the Robot

`robotpy deploy` will deploy all code to the robot. Be sure to be on the same network as the robot.

`.deploy_cfg` contains specific configuration about the deploy process.

Note any folder or file prefixed with a `.` will be skipped in the deploy.

## Linting

"Linting" is the process of checking our code format and style to keep it looking nice

In vsCode, run the lint check via the tasks

`.pylintrc` contains configuration about what checks the linter runs, and what formatting it enforces

## Testing

Run the `Test` configuration in the debugger in vsCode.

## Simulating

Run the `Simulate` configuration in the debugger in vsCode.

## Continuous Integration

Github runs our code on its servers on every commit to ensure our code stays high quality. This is called "Continuous Integration".

`.github/workflows/ci.yml` contains configuration for all the commands that our continuous integration environment.

To minimize frustration and rework, before committing, be sure to:

1. Run the test suite
2. Run linter and fix any formatting errors.

CI will check python 3.11 and 3.12.

## Dependency Management

`pyproject.toml` lists the python packages needed to run the robot code.

`robotpy sync` will ensure the RIO and your development PC have the proper versions of everyhing in `pyproject.toml` installed

`requirements_dev.txt` lists everything needed just for software development. The things in here are not needed to run the code, and therefor should _not_ get installed on a roborio.

Install the development dependencies with `pip install -r requirements_dev.txt`.
