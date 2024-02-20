cd Scripts
call activate.bat
cd ..
coverage run --source=src --module unittest --verbose
coverage report
coverage html
pause