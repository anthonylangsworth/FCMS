set dest=%userprofile%\AppData\Local\EDMarketConnector\plugins\FCMS
rd /s /q %dest% || goto error
mkdir %dest% || goto error
xcopy /y load.py %dest% || goto error
xcopy /y fcms_web_services.py %dest% || goto error

goto end

:error
echo Error %errorlevel%
exit /b %errorlevel%

:end
