# Switch Radio

Simple Alexa skill with Flask-Ask for playing radio stations that are hard to pronounce. 

The Intent Schema has a list of aliases for several radio stations I like to listen to (mostly, but not only Czech ones).
It includes common Alexa ASR errors, too.
The main script has URLs to streams for all the required radio stations.
The skill remembers the last station used for each user.

The `switch_radio.py` script needs to run as a server exposed to the outside, while the `intent_schema.json`
needs to be imported into Amazon Developer Console as a skill.
