# Import setup_virtual_environment
. ${SCRIPT_BASE_PATH}/../Source/Bash/environment/python/setup.sh


install_core_dependencies() {
    install_homebrew

    brew install coreutils
    brew install git
    brew install wget
    brew install warrensbox/tap/tfswitch
    brew cask install postman
    brew cask install pgadmin4
}


remove_core_dependencies() {
    brew cask uninstall pgadmin4
    brew cask uninstall postman
    brew uninstall warrensbox/tap/tfswitch
    brew uninstall wget
    brew uninstall git
    brew uninstall coreutils

    remove_homebrew
}


install_python_tools() {
    install_python

    install_dev_libraries
}


remove_python3_7_tools() {
    remove_python3_7
}


remove_python_tools() {
    remove_dev_libraries

    remove_python
}


install_aws_tools() {
    install_aws_cli

    install_terraform
}


remove_aws_tools() {
    remove_aws_cli

    remove_terraform
}


install_homebrew() {
    echo "### Installing Homebrew ###"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
}


remove_homebrew() {
    echo "### Removing Homebrew ###"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall.sh)"
}


install_node() {
    echo "### Installing Node ###"
    brew install node
}


remove_node() {
    echo "### Removing Node ###"
    brew uninstall node
}


install_python() {
    echo "### Installing Python ###"
    brew install python@3.9
}


remove_python3_7() {
    echo "### Removing Python 3.7 ###"
    brew uninstall python@3.7
}


remove_python() {
    echo "### Removing Python ###"
    brew uninstall python@3.9
}


install_dev_libraries() {
    echo "### Installing development libraries ###"
    brew install swig
}


remove_dev_libraries() {
    echo "### Removing development libraries ###"
    brew uninstall swig
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
    brew install awscli
}


remove_aws_cli() {
    echo "### Removing AWS CLI ###"
    brew uninstall awscli
}


install_terraform() {
    echo "### Installing Terraform ###"
    brew install tfswitch
    brew install terraform-docs

    tfswitch 0.13.7
}


remove_terraform() {
    echo "### Removing Terraform ###"
    brew uninstall terraform-docs
    brew uninstall tfswitch
}
