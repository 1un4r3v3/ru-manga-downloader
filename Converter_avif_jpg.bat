@echo off
chcp 65001
echo Starting conversion process...

for %%F in (*.zip) do (
    echo Processing archive: %%F
    
    mkdir "%%~nF"
    powershell -command "Expand-Archive -Path '%%F' -DestinationPath '%%~nF' -Force"

    del "%%F"
    
    pushd "%%~nF"

    REM Конвертируем все .avif в .jpg и удаляем исходные .avif
    for %%I in (*.avif) do (
        echo Converting: %%I
        magick "%%I" "%%~nI.jpg"
        if exist "%%~nI.jpg" (
            del "%%I"
        )
    )

    REM Удаляем другие лишние файлы
    del /q *.txt
    del /q *.bat
    del /q *.exe
    del /q *.cmd

    popd

    REM Упаковываем обратно в архив
    powershell -command "Compress-Archive -Path '%%~nF\*' -DestinationPath '%%~nF.zip' -Force"

    REM Удаляем распакованную папку
    rmdir /s /q "%%~nF"
    
    echo Finished processing: %%F
)

echo All files have been processed.
pause
