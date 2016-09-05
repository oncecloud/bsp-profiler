
Description
-----------
lhadoop is a self-tuning system for big data analytics.
lhadoop builds on Hadoop while adapting to user needs and system 
workloads to provide good performance automatically, without any 
need for users to understand and manipulate the
many tuning knobs in Hadoop.


Components
----------
1. Profiler: The Profiler uses dynamic instrumentation to learn 
performance models, called job profiles, for unmodified MapReduce programs.
The Profiler also exposes an interface used to analyze past MapReduce executions.

2. What-if Engine: The What-if Engine uses a mix of simulation and model-based 
estimation at the phase level of MapReduce job execution, in order to predict
the performance of a MapReduce job before executed on a Hadoop cluster.
  

4. Visualizer: The Visualizer provides a graphical user interface that allows
the user to (a) analyze past MapReduce job executions, (b) ask hypothetical 
questions regarding the job behavior and, (c) ultimately optimize the job.


Requirements
------------
1. The MapReduce programs must be written using the new Hadoop API
2. The Visualizer requires JavaFX version 1.2.1


Usage:
------
1. To use the Profiler and the other terminal user interfaces, please
   refer to the documentations provided in 'docs'
2. To use the Starfish Visualizer, please refer to 'visualizer/README'


Directories
-----------
- bin:     Contains the Starfish's Command Line Interface
- contrib: Contains various MapReduce programs (compiled separately)
- docs:    Contains usage documentation
- lib:     Contains library jars for compiling the source code
- samples: Contains various sample files
- src:     Contains the source code for the Starfish project
- tools:   Contains profiling and monitoring tools
- visualizer: Contains Starfish's Graphical User Interface (compiled separately)

- build:   Will contain the compiled classes
- btrace:  Will contains the compiled BTrace classes


Compilation
-----------
>> ant
Compiles the entire source code in the 'build' directory and generates the
jar files as well as the BTrace scripts

>> ant test
Executes all available JUnit tests

>> ant javadoc
Generated the javadoc documentation in 'docs/api'

>> ant clean
Deletes the 'build' directory

>> ant help
Prints out all the available ant commands

Notes
-----
The contrib projects and the visualizer are compiled separately using ant.
The ant commands are the same as the above commands, only executed from
within each project's directory.

