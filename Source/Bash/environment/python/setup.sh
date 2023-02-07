setup_python_virtual_environment() {
    environment_path=`realpath $1`

    echo "### Creating Python virtual environment $environment_path ###"
    create_python_virtual_environment $environment_path

    echo "### Installing Python virtual environment dependendencies ###"
    install_python_virtual_environment_dependencies $environment_path
}


create_python_virtual_environment() {
    environment_path=$1
    python_version=$(python3.9 --version | awk '{print $2}' | sed 's/3\.\([0-9][0-9]*\)..*/3.\1/')

    if [[ ! -f "$environment_path/bin/python${python_version}" ]]; then
        echo "Creating virtual environment..."
        python${python_version} -m venv $environment_path
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
    # CFLAGS="-g0 -Wl,--strip-all -I/usr/local/include -L/usr/lib:/usr/local/lib"
    # pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    #     --no-cache-dir \
    #     --compile \
    #     --global-option=build_ext \
    #     --global-option="-j 4" \
    #     -r $environment_path/requirements.txt


    deactivate
}
