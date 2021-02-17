# Fleet Carrier Management System (FCMS) Plug-in

This is based off the Fuel Rats EDMC plug-in, given my inability to find their git repo. I am not the original author. I merely added MSI installer support and decluttered the main window display.

# Installation and Upgrade

Requirements:
1. Install [Elite Dangerous Market Connector (EDMC)](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) version 4.0 or later.

To install:
1. Download the MSI file for the latest release under [Releases](https://github.com/anthonylangsworth/FCMS/releases) at the top right. You may get a warning saying it is potentially harmful. Please ignore these warnings.
2. Run the MSI. This installs the plug-in, upgrading if an earlier version is present. Running the MSI does not require local administrative privileges.
3. Restart EDMC if it was already running.

To configure (only needed once):
1. Open the "File" -> "Settings" menu. This opens the EDMC settings menu.
2. Navigate to the "FCMS" tab. This shows settings for this plug-in.
3. Enter your email address and API key from https://fleetcarrier.space. You can find or create your API key on https://fleetcarrier.space/my_carrier under "Settings".
4. Click OK to close the dialog and save your settings.

See [LICENSE](LICENSE) for the license.

# Limitations

1. The plug-in assumes the commander name in https://fleetcarrier.space is the in-game commander name. If the names differ, modify line 156 in  the "journal_entry" method to modify the commander name. Fix incoming.
2. The discord integration for https://fleetcarrier.space specifies the source system for a carrier jump. However, this plug-in reports the system the commander was in when issuing the jump order. It does not report the carrier's current system.
