#requires -Version 5.1
<#
.SYNOPSIS
Instala dependencias y arranca Cookpad usando el entorno .venv existente.
.EXAMPLE
  .\setup.ps1
.EXAMPLE
  .\setup.ps1 -ProjectRoot 'C:\proyectos\cookpad'
.NOTES
Busca requirements.txt y src\app.py en la carpeta del script o la carpeta
actual y sus respectivas carpetas superiores. No busca en subcarpetas.
No crea un entorno virtual ni modifica un .env existente.
Busca .venv primero junto a la carpeta del proyecto y luego dentro de ella.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# PowerShell 7: usamos nuestros propios mensajes para errores de Python/pip.
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Test-ProjectRoot([string]$Directory) {
    return ((Test-Path -LiteralPath (Join-Path $Directory 'requirements.txt') -PathType Leaf) -and
            (Test-Path -LiteralPath (Join-Path $Directory 'src\app.py') -PathType Leaf))
}

function Find-ProjectRoot {
    foreach ($start in @($PSScriptRoot, (Get-Location).Path)) {
        if ([string]::IsNullOrWhiteSpace($start)) { continue }
        $directory = Get-Item -LiteralPath $start
        while ($null -ne $directory) {
            if (Test-ProjectRoot $directory.FullName) { return $directory.FullName }
            $directory = $directory.Parent
        }
    }
    throw 'No se encontro la raiz. Guarda setup.ps1 junto a requirements.txt y src, o usa -ProjectRoot con la ruta del proyecto.'
}

function Invoke-ProjectPython {
    param([string[]]$PythonArguments, [string]$FailureMessage)
    & $script:PythonExe @PythonArguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (codigo $LASTEXITCODE). Revisa el detalle mostrado arriba."
    }
}

$locationPushed = $false
try {
    if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
        $ProjectRoot = Find-ProjectRoot
    } else {
        $ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
        if (-not (Test-ProjectRoot $ProjectRoot)) {
            throw 'La ruta indicada debe contener requirements.txt y src\app.py.'
        }
    }
    Push-Location -LiteralPath $ProjectRoot
    $locationPushed = $true
    Write-Host "Proyecto: $ProjectRoot" -ForegroundColor Cyan

    $parentDirectory = Split-Path -Path $ProjectRoot -Parent
    $venvCandidates = @()
    if (-not [string]::IsNullOrWhiteSpace($parentDirectory)) {
        $venvCandidates += Join-Path $parentDirectory '.venv\Scripts\python.exe'
    }
    $venvCandidates += Join-Path $ProjectRoot '.venv\Scripts\python.exe'
    $script:PythonExe = $null
    foreach ($candidate in $venvCandidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $script:PythonExe = $candidate
            break
        }
    }
    if ($null -eq $script:PythonExe) {
        throw 'No se encontro .venv\Scripts\python.exe junto a la carpeta del proyecto ni dentro de ella.'
    }
    # Usar directamente este ejecutable evita depender de Activate.ps1 o del PATH.
    Invoke-ProjectPython -PythonArguments @('-c', 'import sys; print(sys.executable); assert sys.prefix != sys.base_prefix') -FailureMessage 'El entorno .venv no funciona'

    Write-Host '[1/4] Comprobando .env...' -ForegroundColor Cyan
    if (Test-Path -LiteralPath '.env' -PathType Leaf) {
        Write-Host 'Se conserva el archivo .env existente.'
    } elseif (Test-Path -LiteralPath '.env') {
        throw '.env existe pero no es un archivo.'
    } elseif (Test-Path -LiteralPath '.env.example' -PathType Leaf) {
        # overwrite=false impide reemplazarlo incluso si se crea al mismo tiempo.
        [System.IO.File]::Copy((Join-Path $ProjectRoot '.env.example'), (Join-Path $ProjectRoot '.env'), $false)
        Write-Warning 'Se creo .env desde .env.example. Revisa sus valores (base de datos, claves y demas configuracion).'
    } else {
        throw 'Faltan .env y .env.example. Crea .env con la configuracion del proyecto y vuelve a ejecutar el script.'
    }

    Write-Host '[2/4] Instalando requirements.txt...' -ForegroundColor Cyan
    Invoke-ProjectPython -PythonArguments @('-m', 'pip', '--version') -FailureMessage 'pip no esta disponible en .venv'
    Invoke-ProjectPython -PythonArguments @('-m', 'pip', 'install', '-r', 'requirements.txt') -FailureMessage 'No se pudieron instalar las dependencias'

    Write-Host '[3/4] Verificando dependencias y aplicacion...' -ForegroundColor Cyan
    Invoke-ProjectPython -PythonArguments @('-m', 'pip', 'check') -FailureMessage 'Hay dependencias incompatibles o faltantes'
    Invoke-ProjectPython -PythonArguments @('-c', 'import fastapi, uvicorn; from src.app import app; assert isinstance(app, fastapi.FastAPI); print(1)') -FailureMessage 'No se pudo importar la API. Revisa .env, requirements.txt y la configuracion de la base de datos'

    Write-Host '[4/4] Iniciando Cookpad...' -ForegroundColor Green
    Write-Host "Documentacion: http://127.0.0.1:$Port/docs"
    Write-Host 'Para detener el servidor: Ctrl+C. Los errores del proceso de recarga aparecen en esta consola.'
    Invoke-ProjectPython -PythonArguments @('-m', 'uvicorn', 'src.app:app', '--reload', '--host', '127.0.0.1', '--port', "$Port") -FailureMessage 'Uvicorn termino con un error'
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if ($locationPushed) { Pop-Location }
}
