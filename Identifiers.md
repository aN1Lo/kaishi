# Message Format #

PROTOCOL:IDENTIFIER:BOUNCE:UID:ORIGIN:MESSAGE

  * Protocol: Integer representing protocol version
  * Identifier: The type of message
  * Bounce: 1 or 0 deciding whether this message should be bounced across the network after being received
  * UID: ID of the message to prevent duplicates being processed
  * Origin: Recoded peerid which started the message chain (: is replaced with ?)
  * Message: Contents of the message

# Example Message #

1:JOIN:1:67.18.89.26?44545:Scalar

# Identifiers #

| **Identifier** | **Usage** |
|:---------------|:----------|
| MSG            | Simple chat message |
| ACTION         | Same as MSG with a different display |
| JOIN           | Informs of a peer joining the network by sending the nickname in the message field and prompts a send of PEERS |
| PEERS          | List of known peers which will be processed by the receiver |
| NICK           | Change of peer nickname |
| PING           | Simple ping message to keep track of which peers are still online |
| DROP           | Drop notice of a peer leaving the network |