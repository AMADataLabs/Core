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

    echo '* libraries/restart-without-asking boolean true' | sudo debconf-set-selections

    apt install -y software-properties-common build-essential curl
}


remove_core_dependencies() {
    apt remove -y software-properties-common build-essential curl
}


install_python_tools() {
    install_pip

    install_python3_7

    install_venv

    # install_pipenv

    install_dev_libraries

    create_base_virtual_environment
}


remove_python_tools() {
    # remove_base_virtual_environments

    remove_dev_libraries

    # remove_pipenv

    remove_venv

    remove_python3_7

    remove_pip
}


install_node() {
    echo "Function 'remove_node not implemented'"

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

    /usr/bin/python3.7 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
}


remove_pip() {
    apt remove -y python3-pip
}


install_python3_7() {
    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" > /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-bionic.list
    apt-key adv --keyserver hkp://keys.gnupg.net:80 --recv-keys BA6932366A755776

    apt install -y python3.7
}


remove_python3_7() {
    apt remove -y python3.7
    apt -y autoremove

    add-apt-repository -r -y ppa:deadsnakes/ppa

    apt remove -y software-properties-common
}


install_venv() {
    apt install -y python3.7-venv
}


remove_venv() {
    apt remove -y python3.6-venv
    apt remove -y python3.7-venv
}


install_pipenv() {
    /usr/bin/python3.7 -m pip install pipenv
}


remove_pipenv() {
    python3 -m pip uninstall -y pipenv
}


install_dev_libraries() {
    echo "### Installing development libraries ###"
    apt install -y python3.7-dev unixodbc-dev
}


remove_dev_libraries() {
    apt remove -y python3.7-dev unixodbc-dev
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

    rm ${ENVIRONMENT_REQUIREMENTS}
    ln -s ${BUILD_REQUIREMENTS} ${ENVIRONMENT_REQUIREMENTS}

    setup_python_virtual_environment Environment/Master
}


remove_base_virtual_environments() {
    rm -rf /home/lane/Development/Python3.6
    rm -rf /home/lane/Development/Python3.7
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
    curl https://tjend.github.io/repo_terraform/repo_terraform.key | sudo apt-key add -
    echo 'deb [arch=amd64] https://tjend.github.io/repo_terraform stable main' > /etc/apt/sources.list.d/terraform.list
    apt update

    apt install -y terraform
}


remove_terraform() {
    echo "### Removing Terraform ###"
    apt remove -y terraform
}
