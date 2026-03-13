getPostRegex="(POST|GET) /[^/]+/"
queryRegex='([A-Za-z_]+=[^& "]+&)+[A-Za-z_]+=[^& "]'

# read tcp dump file
    # | match only lines that include get, post, or query params
    # | split each line on ampersand and print each field on a line
sudo tcpdump -A -s 0 -n -r dump.pcap \
    | grep -E "($getPostRegex)|($queryRegex)" \
    | grep -o -E "[^&]+"
