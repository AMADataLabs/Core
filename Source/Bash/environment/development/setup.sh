# Import setup_virtual_environment
. ${SCRIPT_PATH}/../Source/Bash/environment/python/setup.sh


install_msodbcsql17_driver() {
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt update

    ACCEPT_EULA=Y apt install -y msodbcsql17
}


install_core_dependencies() {
    apt update

    echo '* libraries/restart-without-asking boolean true' | sudo debconf-set-selections

    apt install -y software-properties-common build-essential curl
}


install_python_tools() {
    install_pip

    install_python3_7

    configure_default_python3

    install_venv

    # install_pipenv

    install_dev_libraries

    create_base_virtual_environment
}


install_node() {
    curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodesource_setup.sh

    bash /tmp/nodesource_setup.sh

    rm /tmp/nodesource_setup.sh

    apt install -y nodejs
}


install_aws_tools() {
    install_aws_cli

    install_terraform
}


install_pip() {
    apt install -y python3-pip

    /usr/bin/python3.7 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
}


install_python3_7() {
    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" > /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-bionic.list
    apt-key adv --keyserver hkp://keys.gnupg.net:80 --recv-keys BA6932366A755776

    apt install -y python3.7
}


install_venv() {
    apt install -y python3.7-venv
}


install_pipenv() {
    /usr/bin/python3.7 -m pip install pipenv
}


install_dev_libraries() {
    echo "### Installing development libraries ###"
    apt install -y python3.7-dev unixodbc-dev
}


create_base_virtual_environment() {
    echo "### Setting up master Python virtual environment ###"
    setup_python_virtual_environment Environment/Master
}


install_aws_cli() {
    echo "### Installing AWS CLI ###"
    apt install -y awscli
}


install_terraform() {
    echo "### Installing Terraform ###"
    curl https://tjend.github.io/repo_terraform/repo_terraform.key | sudo apt-key add -
    echo 'deb [arch=amd64] https://tjend.github.io/repo_terraform stable main' > /etc/apt/sources.list.d/terraform.list
    apt update

    apt install -y terraform
}
