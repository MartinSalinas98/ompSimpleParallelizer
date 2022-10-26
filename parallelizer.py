# Necessary imports
import os, sys, subprocess, re

# Declaring global variables
COMPILE_CMD = 'make'        # Compile command
CLEAN_CMD = 'make clean'    # Remove objects and executables command
DEFAULT_N_EXECUTIONS = 5    # Default number of times each code variant will be run to get an average
DEFAULT_N_THREADS = 2       # Default number of threads to modify the source file with after sequential execution

def argparser():
    """
    This function checks input params to provide neccessary variables for the script.
    Returns: source (str), lines (array of int), directives (array of str), numThreads (int), outputFile (str)
    """
    # Defining minimum amount of args to be provided
    MINIMUM_N_ARGS = 2

    # Checking if any arguments have been provided
    if len(sys.argv) < MINIMUM_N_ARGS:
        print("ERROR: Script needs parallelizable file path as argument.\n"
            "\tUse --help for more info.")
        sys.exit(1)
    
    # Display help message
    if len(sys.argv) >= 2 and "--help" in sys.argv:
        print("Parellizer script usage guide:\n")
        print("\t--help:\t\tDisplay this guide.\n")
        print("\t--source:\tPath to parallelizable source file. It can be a relative or absolute path.\n")
        print("\t--lines:\tLines where parallelization should be placed. Only one at a time will be used.\n"
            "\t\t\tLine numbers must be separated with commas without spaces. First line in a file is line 1.\n")
        print("\t--directives:\tPath to file containing parallelization directives. It can be a relative or absolute path.\n"
            "\t\t\tThis file must contain all the parallelization directives, one for each line.\n")
        print("\t--num_threads:\t(Optional) List of new number of threads to set after sequential execution.\n"
            "\t\tThread numbers must be separated with commas without spaces. Each value has to be an integer greater than 1.\n")
        print("\t--save_results:\t(Optional) If used, stdout prints produced by this script will also be saved to a file.\n"
            "\t\tA destination filename must be introduced.\n")
        print("\t--n_executions:\t(Optional) Number of times the script will execute each code variant to get an average.\n"
            "\t\tDefault value is number of executions is 5.\n")
        print("\t--working_dir:\t(Optional) Defines the directory where the makefile and executable files are located.\n"
            "\t\It can be a relative or absolute path.\n")
        print("\t\t\tExample: python3 parallelizer.py --source sourcefile.c --lines 5,6,8 --directives directives.txt --num_threads 2,3,4 --save_results results.txt --n_executions 10 --working_dir mydir/")
        sys.exit(0)
    
    # Checking if input file was provided
    if "--source" not in sys.argv:
        print("ERROR: Source param was not used. Source file is necessary.\n"
            "\tUse --help for more info.")
        sys.exit(1)
    else:
        # Getting index of source file path
        indexOfSource = sys.argv.index("--source") + 1
        # Check if path is provided for source param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfSource].startswith("--"):
            print("ERROR: --source param introduced but no path was provided.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
    
    # Checking if lines param was provided
    if "--lines" not in sys.argv:
        print("ERROR: lines param was not used. Lines to parallelize are necessary.\n"
            "\tUse --help for more info.")
        sys.exit(1)
    else:
        # Getting index of lines to parallelize
        indexOfLines = sys.argv.index("--lines") + 1
        # Check if lines are provided for lines param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfLines].startswith("--"):
            print("ERROR: --lines param introduced but no lines were provided.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        # Checking if all lines are a number
        rawLines = sys.argv[indexOfLines].split(',')
        lines = []
        for line in rawLines:
            if not line.isnumeric():
                print("ERROR: Lines need to be integers separated by commas, but provided {} in {}\n"
                "\tUse --help for more info.".format(line, rawLines))
                sys.exit(1)
            lines.append(int(line))
        # Removing possible duplicates
        lines = list(dict.fromkeys(lines))
    
    # Checking if directives param was provided
    if "--directives" not in sys.argv:
        print("ERROR: directives param was not used. Directive's file to parallelize is necessary.\n"
            "\tUse --help for more info.")
        sys.exit(1)
    else:
        # Getting index of directives to parallelize
        indexOfDirectives = sys.argv.index("--directives") + 1
        # Check if lines are provided for lines param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfDirectives].startswith("--"):
            print("ERROR: --directives param introduced but no directive's file path was provided.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        # Reading directives file and storing results in array
        directives = readFile(sys.argv[indexOfDirectives])
    
    # Checking if num_threads param was provided
    if "--num_threads" in sys.argv:
        # Getting index of num_threads
        indexOfNumThreads = sys.argv.index("--num_threads") + 1
        # Check if lines are provided for lines param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfNumThreads].startswith("--"):
            print("ERROR: --num_threads param introduced but no number of threads was introduced.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        # Checking if all lines are a number
        rawNThreads = sys.argv[indexOfNumThreads].split(',')
        numThreads = []
        for threadN in rawNThreads:
            if not threadN.isnumeric() or int(threadN) < 2:
                print("ERROR: Thread numbers need to be integers greater than 1 separated by commas, but provided {} in {}\n"
                "\tUse --help for more info.".format(threadN, rawNThreads))
                sys.exit(1)
            numThreads.append(int(threadN))
        # Removing possible duplicates
        numThreads = list(dict.fromkeys(numThreads))
    else:
        numThreads = [DEFAULT_N_THREADS]

    # Checking if save_results param was provided
    if "--save_results" in sys.argv:
        # Getting index of save_results
        indexOfSaveResults = sys.argv.index("--save_results") + 1
        # Check if file name was provided for save_results param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfSaveResults].startswith("--"):
            print("ERROR: --save_results param introduced but no output file name was introduced.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        outputFile = os.path.abspath(sys.argv[indexOfSaveResults])
    else:
        outputFile = None
    
    # Checking if n_executions param was provided
    if "--n_executions" in sys.argv:
        # Getting index of n_executions
        indexOfNExecutions = sys.argv.index("--n_executions") + 1
        # Check if number of executions was provided for n_executions param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfNExecutions].startswith("--"):
            print("ERROR: --n_executions param introduced but no number of executions was introduced.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        # Checking that introduced number of executions is actually a number higher than 0
        if not sys.argv[indexOfNExecutions].isnumeric() or int(sys.argv[indexOfNExecutions]) < 1:
            print("ERROR: Number of executions has to be an integer greater than 0.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        nExecutions = int(sys.argv[indexOfNExecutions])
    else:
        nExecutions = DEFAULT_N_EXECUTIONS
    
    # Checking if working_dir param was provided
    if "--working_dir" in sys.argv:
        # Getting index of working_dir
        indexOfWorkingDir = sys.argv.index("--working_dir") + 1
        # Check if file name was provided for working_dir param
        if len(sys.argv) == MINIMUM_N_ARGS or sys.argv[indexOfWorkingDir].startswith("--"):
            print("ERROR: --working_dir param introduced but no working directory path was introduced.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        # If param was provided, arg min count increases by 2
        MINIMUM_N_ARGS += 2
        if not os.path.exists(sys.argv[indexOfWorkingDir]) or not os.path.isdir(sys.argv[indexOfWorkingDir]):
            print("ERROR: Specified path to working directory does not exist or it is not a directory.\n"
                "\tUse --help for more info.")
            sys.exit(1)
        workingDir = os.path.abspath(sys.argv[indexOfWorkingDir])
    else:
        workingDir = None

    return os.path.abspath(sys.argv[indexOfSource]), lines, directives, numThreads, outputFile, nExecutions, workingDir

def showFileError(e):
    """
    This function shows the error displayed when trying to open a file.
    """
    print("ERROR: Cannot open given file. Error is detailed below:\n{}".format(e))
    sys.exit(1)

def readFile(path):
    """
    This function reads a given file and returns its contents in an array of strings,
    where each element is a line of the file.
    Returns: Contents of file (array of str)
    """
    # Trying to read file and return contents
    try:
        file = open(path, "r")
        content = file.read().split('\n')
        file.close()
        return content
    # Check if there are errors opening the file
    except Exception as e:
        showFileError(e)

def execute(source, nExecutions, workingDir):
    """
    This function compiles the source file, runs it, and cleans temporary files.
    Execution is carried out nExecutions times and average result is returned.
    Returns: execution 'Wall time' (str)
    """
    # Getting executable name from source file
    executable = os.path.splitext(source)[0]

    # If a working directory has been set, change to it
    if workingDir:
        os.chdir(workingDir)
    
    # Compile and run given code to get run time nExecutions times
    outputs = []
    for i in range(nExecutions):
        subprocess.run(COMPILE_CMD)
        subprocess.Popen('chmod +x {}'.format(executable).split(), stdout=subprocess.PIPE).communicate()
        output = subprocess.Popen(executable.split(), stdout=subprocess.PIPE).communicate()[0]
        subprocess.Popen(CLEAN_CMD.split(), stdout=subprocess.PIPE).communicate()
        # Formatting and returning output
        for line in output.decode("utf-8").split('\n'):
            if line.startswith('Wall time'):
                outputs.append(int(re.findall(r'\b\d+\b', line)[0]))
                break
    
    return int(sum(outputs)/len(outputs))

def writeFile(path, originalContent, numThreads, codeLine, directive):
    """
    This function writes the new source file with the necessary changes.
    Returns: Nothing
    """
    # Trying to open file and write contents
    try:
        file = open(path, "w")
        for i in range(len(originalContent)):
            # Detecting num threads line to change for new num threads
            if '#define NUM_THREADS' in originalContent[i]:
                file.write("#define NUM_THREADS {}\n".format(numThreads))
                continue
            # Detecting if current line of code is the one where directive will be inserted
            if i +1 == codeLine:
                file.write(directive + '\n')
            # Writing back current line
            file.write(originalContent[i] + '\n')
        file.close()
    # Check if there are errors opening the file
    except Exception as e:
        showFileError(e)

def writeToOriginal(path, originalContent):
    """
    This function writes the source file back to its original state.
    Returns: Nothing
    """
    try:
        file = open(path, "w")
        for line in originalContent:
            file.write(line + '\n')
        file.close()
    # Check if there are errors opening the file
    except Exception as e:
        showFileError(e)

def getOutput(path, mode, string):
    """
    This function displays saves the provided string to stdout and saves it into the given file
    adding it or creating it if an output path is provided.
    """
    # Showing string through stdout
    print(string)

    # If path is provided, save to file
    if path:
        # Opening and writing to output file
        try:
            outputFile = open(path, mode)
            outputFile.write(string + "\n")
            outputFile.close()
        # Check if there are errors opening the file
        except Exception as e:
            showFileError(e)

if __name__ == "__main__":
    # Getting arguments from argparser
    source, lines, directives, numThreadsList, outputPath, nExecutions, workingDir = argparser()

    # Reading source file content
    fileContent = readFile(source)

    # Compile and run original code to get sequential time
    getOutput(outputPath, "w", "Running original source to extract sequential time")
    sequentialTime = execute(source, nExecutions, workingDir)
    getOutput(outputPath, "a", "Sequential time: {}".format(sequentialTime))

    # For each number of threads, for each line selected, run each written directive and get results
    totalResults = []
    for numThreads in numThreadsList:
        threadResults = []
        for codeLine in lines:
            lineResults = []
            for directive in directives:
                # If line is just line break or empty line, skip
                if directive == '' or directive == '\n':
                    continue
                writeFile(source, fileContent, numThreads, codeLine, directive)
                result = execute(source, nExecutions, workingDir)
                getOutput(outputPath, "a", "Results with directive \"{}\" and {} threads in line {}: {} ms".format(directive, numThreads, codeLine, result))
                lineResults.append(result)
            threadResults.append(lineResults)
        totalResults.append(threadResults)
    
    # Write source file back to original state
    writeToOriginal(source, fileContent)

    # Flattening results
    flatResults = []
    for threadResults in totalResults:
        for lineResults in threadResults:
            for runTime in lineResults:
                flatResults.append(runTime)
    
    # Getting fastest run time and index for reference
    fastest = min(flatResults)
    fastestIdx = flatResults.index(fastest)

    # Getting index in original result matrix (totalResults[numThreadsIdx][row][column])
    linesDirsMatrixLen = len(totalResults[0])*len(totalResults[0][0])   # Length of 2D matrix of lines and directives
    numThreadsIdx = int(fastestIdx/linesDirsMatrixLen)                  # Index of lines-directives 2D matrix (index in n_threads array)
    numThreads = numThreadsList[numThreadsIdx]                          # Actual number of threads
    fastestIdxIn2D = fastestIdx-(numThreadsIdx*linesDirsMatrixLen)      # fastest index within its 2D lines and directives matrix
    row = int(fastestIdxIn2D/len(totalResults[0][0]))                   # fastest row index within its 2D lines and directives matrix
    column = fastestIdxIn2D % len(totalResults[0][0])                   # fastest column index within its 2D lines and directives matrix
    getOutput(outputPath, "a", "The best parallelization was obtained with {} threads in line {} using directive \"{}\" with a runtime of {} ms".format(numThreads, lines[row], directives[column], fastest))

    # Calculating speedup and efficiency
    speedup = round(sequentialTime/fastest, 2)
    efficiency = round(speedup/numThreads, 2)
    getOutput(outputPath, "a", "Speedup = Ts/Tp = {}/{} = {}".format(sequentialTime, fastest, speedup))
    getOutput(outputPath, "a", "Efficiency = Speedup/N_Cores = {}/{} = {}".format(speedup, numThreads, efficiency))