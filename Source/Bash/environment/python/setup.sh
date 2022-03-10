setup_python_virtual_environment() {
    environment_path=`realpath $1`

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1

    if [[ ! -f "$environment_path/bin/python3.7" ]]; then
        echo "Creating virtual environment..."
        python3.7 -m venv $environment_path
        echo "Done creating virtual environment"
    else
        echo "Virtual environment already exists."
    fi
}


install_python_virtual_environment_dependencies() {
    environment_path=$1

    . $environment_path/bin/activate

    echo "--- Upgrading pip ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip

    echo "--- Installing Python packages from requirements file $environment_path/requirements.txt ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $environment_path/requirements.txt

    deactivate
}
