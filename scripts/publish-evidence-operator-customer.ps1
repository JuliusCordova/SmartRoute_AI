# Publica evidencias de operador y cliente sin volver a tomar capturas.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$zip = Get-ChildItem -Path (Join-Path $env:USERPROFILE "Downloads") -Filter 'SmartRoute_Evidencias_Operador_Cliente_2026-11-25.zip' -File -Recurse | Select-Object -First 1
if (-not $zip) { throw 'Descarga el ZIP de evidencias en Descargas y vuelve a ejecutar.' }
$dest = Join-Path $env:TEMP 'SmartRoute_Evidencias_Operador_Cliente_2026-11-25'
Expand-Archive -Path $zip.FullName -DestinationPath $dest -Force
$files = @(
    @{ Name = 'OPERADOR_01_Dashboard.png'; Folder = 'docs/evidence/operator' },
    @{ Name = 'OPERADOR_02_Metricas_Rutas.png'; Folder = 'docs/evidence/operator' },
    @{ Name = 'OPERADOR_03_Comparacion_Visual.png'; Folder = 'docs/evidence/operator' },
    @{ Name = 'CLIENTE_01_Seguimiento_Pedido.png'; Folder = 'docs/evidence/customer' }
)
Set-Location $repo
$branchName = git branch --show-current
if ($branchName -ne 'main') { throw "Cambia primero a main (actual: $branchName)." }
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw 'No se pudo sincronizar main.' }
foreach ($item in $files) {
    $src = Join-Path $dest $item.Name
    if (-not (Test-Path $src)) { throw "Falta archivo $($item.Name) en el ZIP." }
    $folder = Join-Path $repo ($item.Folder -replace '/', [IO.Path]::DirectorySeparatorChar)
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    Copy-Item $src (Join-Path $folder $item.Name) -Force
    git add -- "$($item.Folder)/$($item.Name)"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo preparar $($item.Name)." }
}
$staged = git diff --cached --name-only
if (-not $staged) { Write-Host 'Las cuatro capturas ya estaban registradas.'; exit 0 }
git commit -m "docs(evidence): publicar capturas operador y seguimiento cliente"
if ($LASTEXITCODE -ne 0) { throw 'Fallo al crear el commit.' }
git push origin main
if ($LASTEXITCODE -ne 0) { throw 'Fallo al publicar el commit.' }
Write-Host 'OK: las cuatro capturas fueron publicadas en main.'
git status -sb
