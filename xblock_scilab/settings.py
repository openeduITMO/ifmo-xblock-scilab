from path import path

TMP_PATH = path('/tmp/xblock_scilab/')

SCLAB_SERVER_URL = 'http://192.168.4.50:8003'
SCLAB_SERVER_PORT = 8003

# SCILAB_EXEC = path("/opt/scilab-5.5.2/bin/scilab-adv-cli")
SCILAB_EXEC = "scilab-adv-cli"
# SCILAB_HOME = path("/ifmo/app/scilab-5.5.2")
# SCILAB_HOME = path("/ifmo/app/scilab-5.5.2")

SCILAB_STUDENT_SCRIPT = "solution.sce"
SCILAB_INSTRUCTOR_SCRIPT = "checker.sce"
SCILAB_EXEC_SCRIPT = "chdir(\"%s\"); exec(\"%s\");"
