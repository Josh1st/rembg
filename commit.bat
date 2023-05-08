git add -A
set /p message="Enter commit message: "
git commit -m "%message%"
git push -u server master
git push -u origin master
pause