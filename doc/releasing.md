# Release Process

## Prerequisites

1. For MSI installs, download the latest version of the [WiX Toolset](https://wixtoolset.org/releases/) using `dotnet tool install --global wix`.
2. Download and install the WiX UI extension using `wix extension add -g WixToolset.UI.wixext`.
3. (Optional) Have `signtool.exe` in the PATH and the correct digitial certificate in an accessible certificate store.

## Process

1. Update the version in:
    1. `load.py` in the `this.version_info` field on line 23.
    2. `wix\fcms.wxs` in the `<Product>` element on line 4 and `<UpgradeVersion>` elements on lines 7 and 8.
2. Run `buildmsi.cmd` in the `wix` folder to create the MSI.
3. (Optional) Run `wix\signmsi.cmd` to digitally sign the MSI.
4. Install the MSI and test as desired. For reference, the files are installed to `%USERPROFILE%\AppData\Local\EDMarketConnector\plugins\FCMS`.
5. Update documentation, such as [README.md](../README.md).
6. Commit the changes and push to github.
7. Create a new release.
    1. Set the tag to the version number.
    2. Add release comments as appropriate.
    3. Upload the MSI.
8. Publish the release.
