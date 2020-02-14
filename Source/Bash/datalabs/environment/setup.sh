setup_python_virtual_environment() {
    environment_path=$1

    create_python_virtual_environment $environment_path

    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1

    python3 -m venv $environment_path
}


install_python_virtual_environment_dependencies() {
    environment_path=$1

    . $environment_path/bin/activate

    pip install --trusted-host pypi.org --upgrade pip

    pip install --trusted-host pypi.org -r $environment_path/requirements.txt

    deactivate
}
