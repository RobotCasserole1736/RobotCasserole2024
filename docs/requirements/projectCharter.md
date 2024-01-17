# FRC 1736 Python Transition - Summer 2023

## Introduction

FRC Team 1736 is considering switching software development languages from Java to Python. This document describes our decision making process.

## Motivations

FRC 1736 made the decision to use Java for software development over 10 years ago. Much has changed since that time:
* Java is no longer the dominant choice for new software developmet in industry
* Java is no longer used for local high school CS cirriculums 
* The majority of incoming mentors do not know Java
* WPILib has expanded to support languages in many architectures

Additionally, Python is targeted to be officially supported in the 2024 season.

Mentor and Student development time is avaialble over the summer to help execute a transition.

## Benifits

The majority of recent incoming mentors know Python. This is in part because Caterpillar's embedded software stack relies strongly upon python. 
- This streamlines onboarding of new mentors, supporting team goals of mentor recruitment and retention

In turn, knowing python better positions our students for industry internships & collaboration projects (including at Caterpillar)
- This directly supports the goals of our major sponsor

Python is generally regarded as a more "beginner-friendly" language, with less syntax overhead than Java. 
- This should make it easier to onboard new students

Performing any full re-write of the codebase will help build broader ownership
- Fewer "black boxes" in the codebase, which leads to better student and mentor engagement

## Risks & Mitigations

Python retains similar performance concerns to Java - it is not designed for real-time environments.
- However, we're currently living with that constraint without major issues

The team has built up many utilties (simulation, autonomous, website, drive base, etc) in python
- If the transition is done over the summer, with a rigrious schedule, these capiabilties can be rebuilt prior to next season

Less FRC-specific example code is avaialble (new language)
- The team will be relying upon its prior Java knowledge to help translate from examples in one language to another

Python is more prone to runtime errors (duck-typing)
- Will necessitate better linting tools, testing, offboard debugging...

## Alternatives

### Do Nothing

Safest option - allows for continued reusage of all team software libraries & skills. Potentially limits future growth

### Move to C++

Mitigates real-time concerns, also positions students well for industry jobs. Current mentor support is less prevelant than python. Overall learning curve is higher.

### Delay transition until start of 2024 Season

Reduces summer work overhead, at the cost of reduced software delivery capiabilites during the season.

## Must-Have Capiabilities (Based on 2023 robot)

* ~~Normal Git workflow~~
  * Proven in this repo - including CI
* Consistent, "on-size-fits-most" architecture to teach to new students
  * Similar to how we use singletons now
* ~~`@Signal` replacement~~
  * Minimal-overhead way to mark a variable or classmember as "important" and make sure it shows up in Network Tables & log file
  * Proposal - a `log(name, units, value)` method which buffers a value for a paritcular signal. Then, a singleton class which has an `update()` function to pump the value into log files and into NT and log files, all with the same timestamp
* Swerve drive simulation
* ~~Web based dashboard~~
  * No current substitute within WPILib offerings
* ~~Single-step debugger for all targets~~
* ~~Replacement for `Calibration` and its workflow~~
* Faults/ Fix-Me light support
* Replacement for Autonomous sequencer (our own library? re-write? move to command-based?)
  * See [AutoSequencerV2.md](./AutoSequencerV2.md)
* Ability to record runtime errors to disk for offboard debugging
  * Get around unique on-field situations without physically having a development PC hooked up.
  * See https://stackoverflow.com/questions/6598053/python-global-exception-handling for a global exception handler which could write to file?
* ~~Runtime periodic execution duration/frequency metrics~~
* ~~Closed-loop tuning function generator~~
* ~~Interpolating 2d lookup table class~~
* PathPlanner integration
  * https://robotpy.readthedocs.io/projects/pathplannerlib/en/stable/api.html - already done

## Proposed Timeline

### May

* Agreement from Software Team to prioritize this over other things
* Deliverables and finalized timeline

* Proof-of-concept basic setup on tank drive base
  * Need simple auto and teleop modes supported
  * No formal architecture or library delivery required
  * End outputs: "Is this feasible?" and "what are common paint points?"

### June

* Software Library development
* Initial student learning (textbook, "toy projects")

### July

* Record & publish video lessons on Python (from thinkPython) and FRC Robotics
* Library integration on swerve drive base

### August

* Teleop swerve control

### September

* Basic path-following autonomous in Swerve
* Pose estimation through Apriltags

### Oct-Dec

* Training new students

### Jan 2024 

* Deployment into new build season

## Resources

[Support Announcement](https://wpilib.org/blog/bringing-python-to-frc)

[RoboPy Getting Started](https://robotpy.readthedocs.io/en/stable/getting_started.html)

[ThinkPython Textbook](https://greenteapress.com/thinkpython2/thinkpython2.pdf)

[CodeAcademy Python](https://www.codecademy.com/learn/learn-python-3)
