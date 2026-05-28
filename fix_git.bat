@echo off
echo Fixing GitHub submodule issue for frontend folder...

:: 1. Delete the hidden .git folder inside frontend
if exist "frontend\.git" (
    echo Deleting frontend\.git folder...
    rmdir /s /q "frontend\.git"
)

:: 2. Remove the cached submodule link from Git
echo Removing cached submodule link...
git rm --cached frontend

:: 3. Re-add the folder properly
echo Re-adding frontend as a normal folder...
git add frontend

:: 4. Commit the changes
echo Committing the fix...
git commit -m "chore: fix frontend folder submodule tracking issue"

echo.
echo ========================================================
echo FIX COMPLETE! 
echo Now just run: git push
echo And check your GitHub. The folder icon will be normal!
echo ========================================================
pause
