# ompSimpleParallelizer
A simple parallelizer for Open MP

This script is used to parallelize with open mp. It makes a few asumptions:
    - First one is that there is a makefile in the same directory the script is in, set up so running 'make'
      will compile the program generating the executable file.
    - Second, the same makefile has a 'make clean' command that removes object and executable files.
    - Third, you only need to use one directive at a time, not even between multiple lines.
    - Fourth, you have created a text file containing one directive for each line of the file, whose path
      you will send to the script via the --directives param.
    
What this script does:
    - Compiles and runs the original file to get sequential time.
    - After that, parallelization begins. For each line chosen to be parallelized, the script will modify the original
      source file to include a directive from the directives file, and then run it and store the results, also modifying
      the number of threads.
    - Then, the fastest run time will be extracted, referencing the line it parallelized and the directive used for it.
    - Finally, the speedup and efficiency will be calculated with this fastest run time.
