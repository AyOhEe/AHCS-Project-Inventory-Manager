cd Scripts
call activate.bat
cd ..
coverage run --source=src --module unittest discover --verbose --start-directory ./src  --pattern "test_*.py"
coverage report
coverage html
pause