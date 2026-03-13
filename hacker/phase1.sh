echo "Routing Table"
ip route

echo "Scanning ARP table"
echo "arp-scan --interface-enp0s8 --localnet"

echo "Enabling packet forwarding"
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
