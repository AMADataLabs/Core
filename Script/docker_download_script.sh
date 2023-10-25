#/bin/bash 

path="/tmp"

if [ "$(pwd)" != "$path" ]; then
    echo "The current directory is not equal to $path. Changing to $path."
    cd "$path" || exit 1  # Change directory and exit if it fails
fi

#Required dependencies 
sudo apt-get update 
sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release 

#GPG key 
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg 

#Use stable repository for Docker 
echo \ 
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \ 
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 

#Install Docker 
sudo apt-get update 
sudo apt-get -y install docker-ce docker-ce-cli containerd.io 

#Add user to docker group 
sudo groupadd docker 
sudo usermod -aG docker $USER

