@echo off
for /f %%a in ('powershell -command "(Get-Date).DayOfYear"') do set doy=%%a
echo Day of year: %doy%

:: define the "array"
set list=75 76 82 83 96 97 103 104 110 111 124 125 138 139 145 146 152 153 166 167 180 181 187 188 208 209 215 216 243 244 250 251 264 265 278 279 292 293 299 300 313 314 326 327 334 335 341 342

set found=false
for %%i in (%list%) do (
    if "%%i"=="%doy%" set found=true
)

if "%found%"=="true" (
    echo %value% is in the list
    python update.py
    git add data
    git add models
    for /f %%d in ('powershell -command "(Get-Date).ToString(\"yyyy-MM-dd\")"') do set formatted_date=%%d
    git commit -m "Automated update for day %doy% (%formatted_date%)"
    git push
) else (
    echo %value% is NOT in the list
)
