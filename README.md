# FCMS
Fleet Carrier MS plug-in

This is based off the Fuel Rats EDMC plug-in, given my inability to find their git repo. I am not the author of most of this. I merely added some additional debugging code.

To install:
 1. Shut down EDMC.
 2. Navigate to the EDMC plug-ins folder, normally "C:\Users\%username%\AppData\Local\EDMarketConnector\plugins\", replacing "%username%" with your user name.
 3. Create a folder called "FCMS".
 4. Copy the "load.py" file (or a do `git clone`) into the new "FCMS" folder.
 5. Restart EDMC.

Note there is a bug in https://fleetcarrier.space where some commander names
have a "CMDR" prefix. If so, modify line 156 in the "journal_entry" method to
manually prepend "CMDR ".
