# Import setup_virtual_environment
. ${SCRIPT_BASE_PATH}/../Source/Bash/environment/python/setup.sh


install_msodbcsql17_driver() {
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt update

    ACCEPT_EULA=Y apt install -y msodbcsql17
}


remove_msodbcsql17_driver() {
    apt remove -y msodbcsql17

    rm /etc/apt/sources.list.d/mssql-release.list

    keyid=$(apt-key list | grep -B 1 'Microsoft (Release signing) <gpgsecurity@microsoft.com>' | grep -v uid)
    apt-key del $keyid
}


install_core_dependencies() {
    apt update

    echo '* libraries/restart-without-asking boolean true' | debconf-set-selections

    apt install -y software-properties-common build-essential curl
}


remove_core_dependencies() {
    apt remove -y software-properties-common build-essential curl
}


install_python_tools() {
    install_python

    install_pip

    install_venv

    # install_pipenv

    install_dev_libraries
}


remove_python3_7_tools() {
    remove_python3_7_dev_library

    remove_python3_7
}


remove_python_tools() {
    remove_dev_libraries

    # remove_pipenv

    remove_venv

    remove_python3_7

    remove_pip
}


install_node() {
    echo "Function 'install_node not implemented'"

    return 0

    curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodesource_setup.sh

    bash /tmp/nodesource_setup.sh

    rm /tmp/nodesource_setup.sh

    apt install -y nodejs
}


remove_node() {
    echo "Function 'remove_node not implemented'"
}


install_aws_tools() {
    install_aws_cli

    install_terraform
}


remove_aws_tools() {
    remove_aws_cli

    remove_terraform
}


install_pip() {
    apt install -y python3-pip

    python3.9 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
}


remove_pip() {
    apt remove -y python3-pip
}


install_python() {
    add-apt-repository -y ppa:deadsnakes/ppa

    apt install -y python3.9 python3.9-dev
}


remove_python3_7() {
    apt remove -y python3.7 python3.7-dev
    apt -y autoremove

    add-apt-repository -r -y ppa:deadsnakes/ppa

    apt remove -y software-properties-common
}


remove_python() {
    apt remove -y python3.9 python3.9-dev
    apt -y autoremove

    add-apt-repository -r -y ppa:deadsnakes/ppa

    apt remove -y software-properties-common
}


install_venv() {
    apt install -y python3.9-venv
}


remove_venv() {
    apt remove -y python3.9-venv
}


install_pipenv() {
    python3.9 -m pip install pipenv
}


remove_pipenv() {
    python3 -m pip uninstall -y pipenv
}


install_dev_libraries() {
    echo "### Installing development libraries ###"
    apt install -y python3.9-dev unixodbc-dev swig
}


remove_python3_7_dev_library() {
    apt remove -y python3.7-dev
}


remove_dev_libraries() {
    apt remove -y python3.9-dev unixodbc-dev swig
}


create_base_virtual_environment() {
    echo "### Setting up master Python virtual environment ###"
    BUILD_REQUIREMENTS=${SCRIPT_BASE_PATH}/../Build/Master/requirements.txt
    ENVIRONMENT_PATH=${SCRIPT_BASE_PATH}/../Environment/Master
    ENVIRONMENT_REQUIREMENTS=${ENVIRONMENT_PATH}/requirements.txt

    if [[ -d $ENVIRONMENT_PATH ]]; then
        real_directory_path=`realpath ${ENVIRONMENT_PATH}`
        echo "Warning: Environment directory ${real_directory_path} already exists."
    else
        mkdir -p $ENVIRONMENT_PATH
    fi

    rm -f ${ENVIRONMENT_REQUIREMENTS}
    ln -s ${BUILD_REQUIREMENTS} ${ENVIRONMENT_REQUIREMENTS}

    setup_python_virtual_environment Environment/Master
}


install_aws_cli() {
    echo "### Installing AWS CLI ###"
    apt install -y awscli
}


remove_aws_cli() {
    echo "### Removing AWS CLI ###"
    apt remove -y awscli
}


install_terraform() {
    echo "### Installing Terraform ###"
    curl -L https://raw.githubusercontent.com/warrensbox/terraform-switcher/release/install.sh | bash

    tfswitch 0.13.7
}


remove_terraform() {
    echo "### Removing Terraform ###"
    curl -L https://raw.githubusercontent.com/warrensbox/terraform-switcher/release/uninstall.sh | bash
}
