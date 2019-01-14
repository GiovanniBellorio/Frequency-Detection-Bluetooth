sudo vifconfig wlp9s0 down
sudo iwconfig wlp9s0 mode Managed
sudo ifconfig wlp9s0 up
sudo service network-manager stop
sudo service network-manager start
