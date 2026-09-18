Write-Host "Running local test suite..." -ForegroundColor Cyan

# Force execution through the .venv Python 3.11 executable
.\.venv\Scripts\python.exe -m pytest

if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed! Safe to push to Render." -ForegroundColor Green
} else {
    Write-Host "Tests failed! Fix errors before pushing." -ForegroundColor Red
}