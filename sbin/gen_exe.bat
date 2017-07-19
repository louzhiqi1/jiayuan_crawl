@echo off
::生成正式的
pyinstaller --noconsole --onefile ../src/jiayuan.py
mv dist/jiayuan.exe ..
rmdir /S /Q dist
rmdir /S /Q build
::生成测试用的
pyinstaller --console --onefile ../src/jiayuan.py
cd dist
ren jiayuan.exe jiayuan_test.exe
mv jiayuan_test.exe ../..
cd ..
rmdir /S /Q dist
rmdir /S /Q build
pause