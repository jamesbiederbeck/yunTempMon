yunTempMon
by James Biederbeck {james@jamesbiederbeck.com}

This is a python program to read regularly read from the REST API of an Arduino Yun, calculate the temperature, and upload it to If This, Then That.
It is totally usable to just read the temperature, but it can also do so on a loop at a user defined interval, and upload the result to IFTTT.

It's more or less self documenting, between command line usage text, and comments.

You can get the IFTTT applet/recipe/whatever they call it now at:
https://internal-api.ifttt.com/recipes/482776-log-sensor-data-from-arduino-yun-to-a-google-spreadsheet

Sorry about that url.

The script's only real dependency is requests, but that might as well be a core library at this point.

I'll probably regret this later, but feel free to email me if you have any questions.
