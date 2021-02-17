# Introduction

Fleet Carrier Management System (FCMS) is an EDMC plug-in that automatically reports fleet carrier jumps to https://fleetcarrier.space. This tracks fleet carrier movements and locations, optionally back to a squadron Discord.

This is based off the Fuel Rats EDMC plug-in, given my inability to find their git repo. I am not the original author. I merely added an MSI installer and decluttered the main window display.

# Installation and Upgrade

Requirements:
1. Install [Elite Dangerous Market Connector (EDMC)](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) version 4.0 or later.

To install:
1. Download the MSI file for the latest release under the [Releases](https://github.com/anthonylangsworth/FCMS/releases) at the top right. You may get a warning saying it is potentially harmful. Please ignore these warnings.
2. Run the MSI. This installs the plug-in, upgrading if an earlier version is present. Running the MSI does not require local administrative privileges.
3. Restart EDMC if it was already running.

# Use

To configure (only needed once):
1. Run EDMC.
2. Open the "File" -> "Settings" menu. This opens the EDMC settings menu.
3. Navigate to the "FCMS" tab. This shows settings for this plug-in.
4. Enter your email address and API key from https://fleetcarrier.space. You can find or create your API key on https://fleetcarrier.space/my_carrier under the "Settings" tab on the right.
5. Click OK to close the dialog and save your settings.

To use:
1. Start EDMC before you jump your fleet carrer, if not when you start playing **Elite: Dangerous**.
2. Operate your fleet carrier as normal.
3. The FCMS plug-in automatically updates https://fleetcarrier.space with your fleet carrier movements.

See [LICENSE](LICENSE) for the license. There was no license included with the original source code.

# Limitations

1. The plug-in assumes the commander name in https://fleetcarrier.space is the in-game commander name. If the names differ, modify line 156 in  the "journal_entry" method to modify the commander name. Fix incoming.
2. The discord integration for https://fleetcarrier.space specifies the source system for a carrier jump. However, this plug-in reports the system the commander was in when issuing the jump order. It does not report the carrier's current system.
