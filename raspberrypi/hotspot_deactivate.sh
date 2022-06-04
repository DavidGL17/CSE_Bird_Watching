sudo systemctl stop dnsmasq 
sudo systemctl stop hostapd
sudo systemctl mask hostapd
sudo systemctl disable hostapd
sudo cp pi_config_files/dhcpcd_no_wifi.conf /etc/dhcpcd.conf
sudo cp pi_config_files/hostapd_no_wifi /etc/default/hostapd
sudo reboot 0