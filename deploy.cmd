set dest=%userprofile%\AppData\Local\EDMarketConnector\plugins\FCMS
rd /s /q %dest%
mkdir %dest%
xcopy /y load.py %dest%
