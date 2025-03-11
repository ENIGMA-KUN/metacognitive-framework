# PowerShell script to setup and upload to GitHub
# Save this as setup_github.ps1 in your project root directory

# Configuration - Change these values as needed
$repoName = "metacognitive-framework"
$username = "enigma-kun"
$email = "csking007kog@gmail.com" 
$description = "Metacognitive Analysis Framework for evaluating LLM reasoning capabilities"

# Set up Git configuration
git config --global user.name $username
git config --global user.email $email

# Create necessary directories
$dirs = @(
    "metacognitive_framework/data/problems",
    "metacognitive_framework/data/mock_responses", 
    "metacognitive_framework/data/results"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created directory: $dir"
    }
    
    # Add .gitkeep file to track empty directory
    $gitkeepPath = Join-Path $dir ".gitkeep"
    if (!(Test-Path $gitkeepPath)) {
        New-Item -ItemType File -Force -Path $gitkeepPath | Out-Null
        Write-Host "Created .gitkeep in: $dir"
    }
}

# Create .gitignore file if it doesn't exist
$gitignorePath = ".gitignore"
if (!(Test-Path $gitignorePath)) {
    # Add your .gitignore content here
    $gitignoreContent = @"
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Virtual environments
env/
venv/
ENV/
env.bak/
venv.bak/

# VS Code settings
.vscode/
.idea/

# API keys and sensitive data
.env
*.key

# Project specific
data/mock_responses/*.json
data/results/*
data/problems/*.json
"@
    
    Set-Content -Path $gitignorePath -Value $gitignoreContent
    Write-Host "Created .gitignore file"
}

# Initialize git repository if not already initialized
if (!(Test-Path ".git")) {
    git init
    Write-Host "Initialized Git repository"
}

# Add all files to the staging area
git add .
Write-Host "Added files to staging area"

# Commit the changes
git commit -m "Initial commit: Metacognitive Analysis Framework"
Write-Host "Committed files"

# Add GitHub as the remote origin
git remote add origin "https://github.com/$username/$repoName.git"
Write-Host "Added GitHub remote"

# Push to GitHub
Write-Host "Pushing to GitHub..."
git push -u origin master

# Check for success
if ($LASTEXITCODE -eq 0) {
    Write-Host "Code successfully uploaded to GitHub at: https://github.com/$username/$repoName"
} else {
    Write-Host "There was an issue pushing to GitHub. You may need to:"
    Write-Host "1. Create the repository at https://github.com/new first"
    Write-Host "2. Use a personal access token if you're having authentication issues"
    Write-Host "3. If your default branch is 'main' instead of 'master', use:"
    Write-Host "   git branch -M main"
    Write-Host "   git push -u origin main"
}