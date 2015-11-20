# 開始 #
kaishi is a chat program without any central servers.  Currently all users connected to kaishi are on the same level of the network, meaning no user has more control over the others.  kaishi also contains a minimalistic IRC server which you can use rather than directly communicating with the console.  After starting the program, type /irc to start the server.  Then, connect to 127.0.0.1:44546

Messages and /me's work in the IRC server, as well as /peers /clearpeers and /nick.  The rest of  kaishi's commands still need to be entered in the console window.

If you are having difficulty staying connected, make sure port 44545 is allowing incoming transfer.

### Is kaishi anonymous? ###
No, kaishi does not take any measures to establish anonymity between peers.

### Are kaishi's messages encrypted? ###
No.  While kaishi does compress messages before dispatching them across the network, anyone who is able to sniff the packets would be able to easily decompress and read them.

### Can I use kaishi to exchange illegal content? ###
Yes, you can, just like any other public resource.  However, it is strongly recommend you take the above into account before considering doing so.