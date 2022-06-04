sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y dnsmasq hostapd
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp dhcpcd_wifi.conf /etc/dhcpcd.conf
sudo service dhcpcd restart
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo systemctl start dnsmasq
sudo cp hostapd_wifi.conf /etc/hostapd/hostapd.conf
sudo cp hostapd_wifi /etc/default/hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd