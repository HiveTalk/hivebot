# hivebot
hivetalk nostr bot - room announcer

- This Bot will poll the HiveTalk API every 15 min do the following: 
- It will post a link to active rooms within the last hour on the nostr social media account as a kind 1 note.
- It will also append it to the log in this repository. 
- If the room has been posted in the last hour already it will not repost it so as not to spam the network.

TODO SimpleX:  
- Make a SimpleX bot that posts notifications of rooms when created and destroyed.
- In Simplex Bot, Allow users to poll specific rooms which are public and unlocked to see who is in the room

TODO Nostr:
- Kind 1 note should be revised and posted as live event, as a push notification, when wss API endpoint is available.
- Live Events on nostr should be updated when event is over.
  

Bot and social account now consolidated on nostr, should post to 
https://njump.me/npub1z0lcg9p2v5nzg5fycxq0k56ze6snp42clmrafzqpn5w6u74v5x9q708ldk
