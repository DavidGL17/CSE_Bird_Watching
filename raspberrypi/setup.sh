sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y dnsmasq hostapd git nmap python3-pip chromium-chromedriver xvfb caddy
pip install -r requirements.txt
echo "starting hotspot activation..."
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp pi_config_files/dhcpcd_wifi.conf /etc/dhcpcd.conf
sudo service dhcpcd restart
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cp pi_config_files/dnsmasq.conf /etc/dnsmasq.conf
sudo systemctl start dnsmasq
sudo cp pi_config_files/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp pi_config_files/hostapd_wifi /etc/default/hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd