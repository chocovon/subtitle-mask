set "projectName=Subtitle Mask"

pyinstaller -w -D --name "%projectName%" main.py

set "sourceFolder=./dist/%projectName%"
set "zipFile=./dist/%projectName%.zip"
7z a -tzip "%zipFile%" "%sourceFolder%"
