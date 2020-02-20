To Initialize the environment you must have Python 3.7 installed on your system in a Linux Environment.

Run the following the first time you clone this project:

python3.7 -m venv DjangoPPD
source DjangoPPD/bin/activate

Then go to the directory where your requirements file is(the cloned repo has this).

Run this:

pip3 install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org -r requirements.txt 


When you work in the environment again all you need to do is activate the virtual environment again:

source DjangoPPD/bin/activate




