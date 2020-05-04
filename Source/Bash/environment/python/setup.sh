setup_python_virtual_environment() {
    environment_path=`realpath $1`

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_environment_directory() {
    mkdir ${SCRIPT_BASE_PATH}/../Environment/${PROJECT_NAME}
}


link_to_requirements_file() {
    ln -s ${SCRIPT_BASE_PATH}/../Build/${PROJECT_NAME}/requirements.txt ${SCRIPT_BASE_PATH}/../Environment/${PROJECT_NAME}/requirements.txt
}


create_python_virtual_environment() {
    environment_path=$1

    python3 -m venv $environment_path
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
