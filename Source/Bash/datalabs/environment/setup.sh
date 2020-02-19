setup_python_virtual_environment() {
    environment_path=$1

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1

    python3 -m venv $environment_path
}


install_python_virtual_environment_dependencies() {
    environment_path=$1

    . $environment_path/bin/activate

    which pip

    echo "--- Upgrading pip ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip

    echo "--- Installing Python packages from requirements file $environment_path/requirements.txt ---"
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $environment_path/requirements.txt

    deactivate
}
