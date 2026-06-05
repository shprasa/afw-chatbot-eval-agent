# 120 Original Style Short personas — Claude host, System Prompt v1 (server-side).
# Partner must have v1 deployed on the Claude app.
#
# Run:  .\run_original_style_short_claude.ps1
# Resume:  .\run_original_style_short_claude.ps1 -Resume

param([switch]$Resume)

Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PY = "$env:USERPROFILE\anaconda3\python.exe"

$transcript = Join-Path (Split-Path $PSScriptRoot -Parent) "artifacts\chatbot_live_transcripts_original_style_short_claude.jsonl"

$env:CHATBOT_WEB_BASE_URL = "https://angel-flight-chatbot-claude.azurewebsites.net"
$env:CHATBOT_BACKEND = "claude"
$env:CHATBOT_DATASET_XLSX = Join-Path (Split-Path $PSScriptRoot -Parent) "data\AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
$env:CHATBOT_DATASET_SHEET = "120_test_cases"
$env:CHATBOT_OUTPUT_SUFFIX = "_original_style_short_claude"
$env:CHATBOT_SOURCE_TAG = "original_style_short_f_claude"
$env:CHATBOT_SSL_VERIFY = "0"
$env:CHATBOT_PARALLEL_WORKERS = "4"
$env:CHATBOT_TURN_PAUSE_S = "0.35"
$env:CHATBOT_TIMEOUT_S = "120"
$env:CHATBOT_MAX_RETRIES = "4"

Remove-Item Env:CHATBOT_USE_120_DATASET -ErrorAction SilentlyContinue
Remove-Item Env:CHATBOT_EVAL_LIMIT -ErrorAction SilentlyContinue

if ($Resume) {
    $env:CHATBOT_RESUME = "1"
    Write-Host "Resume mode: skipping personas already scored in transcript." -ForegroundColor Yellow
} else {
    Remove-Item Env:CHATBOT_RESUME -ErrorAction SilentlyContinue
    if (Test-Path $transcript) {
        Write-Host "Removing prior transcript for fresh run: $transcript"
        Remove-Item $transcript -Force
    }
}

Write-Host "Claude endpoint: $env:CHATBOT_WEB_BASE_URL"
Write-Host "System prompt: v1 (must be active on Claude deployment)"
Write-Host "Dataset: $env:CHATBOT_DATASET_XLSX"
Write-Host "Outputs suffix: $env:CHATBOT_OUTPUT_SUFFIX"
Write-Host ""

& $env:PY (Join-Path $PSScriptRoot '..\src\chatbot_live_eval.py')
