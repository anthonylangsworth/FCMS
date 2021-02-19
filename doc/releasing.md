# Release Process

## Prerequisites

1. For MSI installs, download the latest version of the [WiX Toolset](https://wixtoolset.org/releases/).
2. Ensure the WiX Toolset bin folder, `%ProgramFiles(x86)%\WiX Toolset v3.11\bin\` by default, is in the PATH.
3. (Optional) Have `signtool.exe` in the PATH and the correct digitial certificate in an accessible certificate store.

## Process

1. Update the version in:
    1. `load.py` in the `this.version` field on line 16.
    2. `wix\edmfat.wxs` in the `<Product>` element on line 3 and `<UpgradeVersion>` elements on lines 8 and 9.
2. Run `wix\buildmsi.cmd` to create the MSI.
3. (Optional) Run `wix\signmsi.cmd` to digitally sign the MSI.
4. Install the MSI and test as desired. For reference, the files are installed to `%USERPROFILE%\AppData\Local\EDMarketConnector\plugins\EDMFAT`.
5. Update documentation, such as [README.md](../README.md).
6. Commit the changes and push to github.
7. Create a new release.
    1. Set the tag to the version number.
    2. Add release comments as appropriate.
    3. Upload the MSI.
8. Publish the release.
