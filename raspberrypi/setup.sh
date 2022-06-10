sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y dnsmasq hostapd git nmap wget
echo "starting hotspot activation..."
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp pi_config_files/dhcpcd_wifi.conf /etc/dhcpcd.conf
sudo service dhcpcd restart
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cp pi_config_files/dnsmasq.conf /etc/dnsmasq.conf
sudo systemctl start dnsmasq
sudo cp pi_config_files/hostapd_wifi.conf /etc/hostapd/hostapd.conf
sudo cp pi_config_files/hostapd_wifi /etc/default/hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd