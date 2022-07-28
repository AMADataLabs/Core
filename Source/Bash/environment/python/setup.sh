PYTHON_VERSION=3.7


setup_python_virtual_environment() {
    environment_path=`realpath $1`

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1

    which python3.9

    if [[ $? -eq 0 ]]; then
        PYTHON_VERSION=3.9
    fi

    if [[ ! -f "$environment_path/bin/python${PYTHON_VERSION}" ]]; then
        echo "Creating virtual environment..."
        python${PYTHON_VERSION} -m venv $environment_path
        echo "Done creating virtual environment"
    else
        echo "Virtual environment already exists."
    fi
}


install_python_virtual_environment_dependencies() {
    environment_path=$1

    . $environment_path/bin/activate

    pip config set global.index-url https://pypi.org/simple

    echo "--- Upgrading pip ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip

    echo "--- Installing Python packages from requirements file $environment_path/requirements.txt ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $environment_path/requirements.txt

    deactivate
}
