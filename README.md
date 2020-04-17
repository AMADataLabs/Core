# HSG Data Labs Repository Overview

There are currently six top-level folders in this repository: *Build*, *Environment*, *Sandbox*, *Script*, *Source*, and *Test*. For day-to-day development, no additional top-level files or folders should be created. When in doubt, create a project sub-folder under *Sandbox/* and store your code there.

In *Sandbox/* and in general, please adhere to the camel-case project folder naming convention for consistency.

Additional details about each of these folders follows.

## Build

This folder stores configuration files related to building deployable code. Currently what that means is that Dockerfiles are created here per project.

## Environment

In general, each project has its own set of Python dependencies. These dependencies should be derived from those of the Master environment in *Environment/Master/requirements.txt* and defined in *Environment/<Project Name>/requirements.txt*. This allows for either a virtual environment or a docker image to be created that can consistently run the project's Python code.

## Sandbox

As imiplied above, *Sandbox/* is used to put unshared code for a project that is a work in progress. Ideally, reusable code will be transfered to the *Source/* folder so that other projects can benefit from previous work. In addition, code that will be employed in a production application must first be transitioned to *Source/*.

## Script

Any scripts used to maintain the repository, build or deploy applications, or aid users in doing their work should be stored in *Script/*. Scripts associated with a particular project should be stored in a project sub-folder identically named to the project folder under *Sandbox/*, *Environment/*, and *Build/*. A brief description of the scripts follows.

### create-project

Use this script to create initial build and environment files for a project. The only required argument is the name of the project. A second argument is a comma-separated list of Python dependencies from the master dependency list to include (by default all dependencies are included).

### genenv.py

Used by create-project to generate the dependencies configuration file for the project environment.

### run.py

A helper Python script that adds the *Source/* folder to the Python search path before running what was specified in the arguments.

### setup-development-environment

Create an initial Python development environment. This script assumes the user is working inside the Ubuntu 18.04 version of the Windows Subsystem for Linux (WSL).

### setup-python-virtual-environment

This script creates a Python virtual environment for a project and installs the dependencies in the project's requirements.txt file.

### setup-repository / setup_repository.py

The Python script and its BASH wrapper generate `.env` files from `dotenv_template.txt` files in all `Sandbox/*` directories. See the *Local Environment Setup* section for more details.

### start-ssh-agent

This is a helper script for starting an *ssh-agent* process and configuring the user's environment to reconnect to the process when a new WSL terminal is started.

### wipe-development-environment

This reverses (most) of the changes made by *setup-development-environment*. It is mostly used for testing the setup script.

## Source

Shared source code should be put into the language sub-folder of *Source/* (i.e. Python code lives in *Source/Python/*).

### Python

Python package folders should all start with *Source/Python/datalabs/* (i.e. all Data Labs packages start with *datalabs.*).

## Test

Not surprisingly, all test code should be put in this folder. The folder and file structure mirrors that of *Source/* with some exceptions.

### Python

The Pytest tool is used for running Python test code.  Due to how Pytest looks for test code, tests for a particular module should be put in a module of the same name but with the *test_* prefix. Furthermore, in order to avoid any module name clashes, the *test* package is inserted under *datalabs*. Otherwise the package structure mirrors that of *Source/Python/datalabs/*. For example, unit tests for the module *Source/Python/datalabs/environment/setup.py* are defined in *Test/Python/datalabs/test/environment/test_setup.py*.

Additional supporting test code can be added as needed in modules without a *test_* prefix.


# Local Environment Setup

In order to find Data Labs Python modules when developing code, the `PYTHONPATH` needs to be set. A system of per-project `settings.py` modules and `.env` template files is used to bootstrap the `PYTHONPATH` for Sandbox applications.

Manually or using the `create-project` script, a copy of the `settings.py` and `dotenv_template.py` files from `Environment/Master` should be added and committed to every new Sandbox project. The `PROJECT_NAME` variable should be set to the name of the directory in `dotenv_template.py` Any necessary configuration customizations should also be done in the template file. Credentials should not be added at this time, although credential variables with placeholder values can be added and removed as needed to/from the template file for a particular project.

Running the `setup_repository.py` script will find all `dotenv_template.txt` Jinja template files in `Sandbox/*` directories, resolve their `DATALABS_PYTHONPATH` variables, and generate `.env` configuration files for each template. Any application in that directory can then `import settings`, after which all Python modules under the `datalabs` package tree will be available for importing. Temporarily the PYTHONPATH also includes `Sandbox/CommonCode/` and `Sandbox/CommonModelCode/` in addition to `Source/Python` until such time all shared code is migrated into `Source/Python/`.
