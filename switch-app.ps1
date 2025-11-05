# Script para cambiar entre app.py y app_refactored.py
# Uso: .\switch-app.ps1 [original|refactored]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("original", "refactored")]
    [string]$Version = "refactored"
)

Write-Host "🔄 Cambiando a versión: $Version" -ForegroundColor Cyan

if ($Version -eq "refactored") {
    $flaskApp = "app_refactored.py"
    $gunicornApp = "app_refactored:app"
    Write-Host "✅ Usando app_refactored.py (versión refactorizada)" -ForegroundColor Green
} else {
    $flaskApp = "app.py"
    $gunicornApp = "app:app"
    Write-Host "✅ Usando app.py (versión original)" -ForegroundColor Yellow
}

# Actualizar Dockerfile
$dockerfileContent = Get-Content Dockerfile -Raw
$dockerfileContent = $dockerfileContent -replace 'FLASK_APP=app.*\.py', "FLASK_APP=$flaskApp"
$dockerfileContent = $dockerfileContent -replace 'app.*:app', $gunicornApp
$dockerfileContent | Set-Content Dockerfile -NoNewline

# Actualizar Dockerfile.dev
$dockerfileDevContent = Get-Content Dockerfile.dev -Raw
$dockerfileDevContent = $dockerfileDevContent -replace 'FLASK_APP=app.*\.py', "FLASK_APP=$flaskApp"
$dockerfileDevContent = $dockerfileDevContent -replace 'python.*app.*\.py', "python $flaskApp"
$dockerfileDevContent | Set-Content Dockerfile.dev -NoNewline

# Actualizar docker-compose.yml
$composeContent = Get-Content docker-compose.yml -Raw
$composeContent = $composeContent -replace 'FLASK_APP=app.*\.py', "FLASK_APP=$flaskApp"
$composeContent | Set-Content docker-compose.yml -NoNewline

Write-Host "`n✅ Archivos actualizados. Reconstruye Docker con:" -ForegroundColor Green
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host "   docker-compose up -d --build" -ForegroundColor White

