# ompSimpleParallelizer
A simple parallelizer for Open MP.

**This script is used to parallelize with open mp. It makes a few asumptions:**<br>
- First one is that there is a makefile set up so running 'make' will compile the program generating the executable file.<br>
- Second, the same makefile has a 'make clean' command that removes object and executable files.<br>
- Third, you only need to use one directive at a time, not even between multiple lines.<br>
- Fourth, you have created a text file containing one directive for each line of the file, whose path you will send to the script via the --directives param.<br>
    
**What this script does:**<br>
- Compiles and runs the original file to get sequential time.<br>
- After that, parallelization begins. For each line chosen to be parallelized, the script will modify the original source file to include a directive from the directives file, and then run it and store the results, also modifying the number of threads.<br>
- Then, the fastest run time will be extracted, referencing the line it parallelized and the directive used for it.<br>
- Finally, the speedup and efficiency will be calculated with this fastest run time.<br>

**Script usage params:**<br>
&emsp;*--help*:&emsp;&emsp;&emsp;&emsp;Display this guide.<br>
&emsp;*--source*:&emsp;&emsp;&emsp;Path to parallelizable source file. It can be a relative or absolute path.<br>
&emsp;*--lines*:&emsp;&emsp;&emsp;&emsp;Lines where parallelization should be placed. Only one at a time will be used.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Line numbers must be separated with commas without spaces. First line in a file is line 1.<br>
&emsp;*--directives*:&emsp;&ensp;&nbsp;Path to file containing parallelization directives. It can be a relative or absolute path.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;This file must contain all the parallelization directives, one for each line.<br>
&emsp;*--num_threads*: (Optional) List of new number of threads to set after sequential execution.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Thread numbers must be separated with commas without spaces. Each value has to be an integer greater than 1.<br>
&emsp;*--save_results*:&ensp;(Optional) If used, stdout prints produced by this script will also be saved to a file.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;A destination filename must be introduced.<br>
&emsp;*--n_executions*: (Optional) Number of times the script will execute each code variant to get an average.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;Default value is number of executions is 5.<br>
&emsp;*--working_dir*:&emsp;(Optional) Defines the directory where the makefile and executable files are located.<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;It can be a relative or absolute path.<br><br>
**Example:**<br>`python3 parallelizer.py --source sourcefile.c --lines 5,6,8 --directives directives.txt --num_threads 2,3,4 --save_results results.txt --n_executions 10 --working_dir mydir/`
