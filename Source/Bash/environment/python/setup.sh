setup_python_virtual_environment() {
    environment_path=`realpath $1`

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1

    /usr/bin/env python3.7 -m venv $environment_path
    echo "Done creating virtual environment"
}


install_python_virtual_environment_dependencies() {
    environment_path=$1

    echo Still using $(which python3.7)
    current_path=$PATH
    export VIRTUAL_ENV=${PWD}/Environment/Master/BitBucketPipelines
    echo Adjusting path to use $VIRTUAL_ENV/bin/python3.7
    export PATH="$VIRTUAL_ENV/bin:$PATH"
    echo Now using $(which python3.7)

    echo "--- Upgrading pip ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip

    echo "--- Installing Python packages from requirements file $environment_path/requirements.txt ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $environment_path/requirements.txt

    unsetenv VIRTUAL_ENV
    export PATH=$current_path
}
