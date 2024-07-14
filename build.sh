git fetch --all && git reset --hard origin/<branch-name> && git pull
sudo docker build -t private-assistant .
sudo docker tag private-assistant 0x2196f3/private-assistant:latest
sudo docker run -d --name=private-assistant --restart=always --privileged=true -v ../private-assistant-config/config:/config 0x2196f3/private-assistant