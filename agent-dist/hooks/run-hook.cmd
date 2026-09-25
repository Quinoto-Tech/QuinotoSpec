:; exec bash "$(dirname "$0")/session-start.sh" "$@"
@echo off
setlocal
set "PLUGIN_ROOT=%~dp0.."
where bash >nul 2>&1
if errorlevel 1 (
    echo bash not found >&2
    exit /b 1
)
bash "%~dp0session-start.sh" --platform claude %*
set "RC=%ERRORLEVEL%"
exit /b %RC%
