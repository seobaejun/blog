# Firebase Functions Deployment Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Firebase Functions Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check current path
$currentPath = Get-Location
Write-Host "Current path: $currentPath" -ForegroundColor Green
Write-Host ""

# Check Firebase CLI
Write-Host "[1/3] Checking Firebase CLI..." -ForegroundColor Yellow
try {
    $firebaseVersion = firebase --version 2>&1
    Write-Host "Firebase CLI version: $firebaseVersion" -ForegroundColor Green
} catch {
    Write-Host "Firebase CLI not installed. Installing..." -ForegroundColor Yellow
    npm install -g firebase-tools
}

Write-Host ""

# Check Firebase login
Write-Host "[2/3] Checking Firebase login..." -ForegroundColor Yellow
firebase projects:list 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Firebase login required. Please login..." -ForegroundColor Red
    firebase login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Login failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Firebase login confirmed" -ForegroundColor Green
}

Write-Host ""

# Set project
Write-Host "[3/3] Setting Firebase project..." -ForegroundColor Yellow
firebase use blog-cdc9b
if ($LASTEXITCODE -ne 0) {
    Write-Host "Project setup failed" -ForegroundColor Red
    exit 1
}
Write-Host "Project setup completed" -ForegroundColor Green

Write-Host ""

# Check and install functions-framework locally for discovery
Write-Host "[4/5] Checking functions-framework..." -ForegroundColor Yellow
try {
    python -c "import functions_framework" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing functions-framework..." -ForegroundColor Yellow
        pip install functions-framework 2>&1 | Out-Null
    }
    Write-Host "✓ functions-framework ready" -ForegroundColor Green
} catch {
    Write-Host "Installing functions-framework..." -ForegroundColor Yellow
    pip install functions-framework 2>&1 | Out-Null
    Write-Host "✓ functions-framework installed" -ForegroundColor Green
}

Write-Host ""

# Copy required directories to firebase_functions
Write-Host "[5/5] Preparing Functions directory..." -ForegroundColor Yellow
$functionsDir = Join-Path $currentPath "firebase_functions"
$adminWebDir = Join-Path $currentPath "admin_web"
$srcDir = Join-Path $currentPath "src"

# Copy admin_web directory
if (Test-Path $adminWebDir) {
    $adminWebDest = Join-Path $functionsDir "admin_web"
    if (Test-Path $adminWebDest) {
        Remove-Item $adminWebDest -Recurse -Force
    }
    Copy-Item $adminWebDir -Destination $adminWebDest -Recurse -Force
    Write-Host "✓ admin_web directory copied" -ForegroundColor Green
} else {
    Write-Host "✗ admin_web directory not found" -ForegroundColor Red
}

# Copy src directory
if (Test-Path $srcDir) {
    $srcDest = Join-Path $functionsDir "src"
    if (Test-Path $srcDest) {
        Remove-Item $srcDest -Recurse -Force
    }
    Copy-Item $srcDir -Destination $srcDest -Recurse -Force
    Write-Host "✓ src directory copied" -ForegroundColor Green
} else {
    Write-Host "✗ src directory not found" -ForegroundColor Red
}

Write-Host ""

# Deploy Functions and Hosting
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Functions and Hosting deployment..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "This may take a few minutes." -ForegroundColor Yellow
Write-Host ""

firebase deploy --only "functions,hosting"

# Clean up copied directories
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
$adminWebDest = Join-Path $functionsDir "admin_web"
$srcDest = Join-Path $functionsDir "src"
if (Test-Path $adminWebDest) {
    Remove-Item $adminWebDest -Recurse -Force
}
if (Test-Path $srcDest) {
    Remove-Item $srcDest -Recurse -Force
}
Write-Host "✓ Cleanup completed" -ForegroundColor Green

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "Deployment completed!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Functions URL:" -ForegroundColor Yellow
    firebase functions:list
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Deployment failed" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
Read-Host
