sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp pi_config_files/dhcpcd_wifi.conf /etc/dhcpcd.conf
sudo service dhcpcd restart
sudo systemctl start dnsmasq
sudo cp pi_config_files/hostapd_wifi /etc/default/hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd