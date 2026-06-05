# F001-F120 Original Style Short — live OpenAI eval (user messages only)
# Run:  .\run_original_style_short_eval.ps1
# Resume:  .\run_original_style_short_eval.ps1 -Resume

param([switch]$Resume)

Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PY = "$env:USERPROFILE\anaconda3\python.exe"

$env:CHATBOT_DATASET_XLSX = Join-Path (Split-Path $PSScriptRoot -Parent) "data\AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
$env:CHATBOT_DATASET_SHEET = "120_test_cases"
$env:CHATBOT_OUTPUT_SUFFIX = "_original_style_short_openai"
$env:CHATBOT_SOURCE_TAG = "original_style_short_f"
$env:CHATBOT_SSL_VERIFY = "0"
$env:CHATBOT_PARALLEL_WORKERS = "6"
$env:CHATBOT_TURN_PAUSE_S = "0.3"

Remove-Item Env:CHATBOT_USE_120_DATASET -ErrorAction SilentlyContinue
Remove-Item Env:CHATBOT_EVAL_LIMIT -ErrorAction SilentlyContinue

if ($Resume) {
    $env:CHATBOT_RESUME = "1"
    Write-Host "Resume mode: skipping personas already in transcript jsonl." -ForegroundColor Yellow
} else {
    Remove-Item Env:CHATBOT_RESUME -ErrorAction SilentlyContinue
    $transcript = Join-Path (Split-Path $PSScriptRoot -Parent) "artifacts\chatbot_live_transcripts_original_style_short_openai.jsonl"
    if (Test-Path $transcript) {
        Write-Host "Removing prior transcript for fresh run: $transcript"
        Remove-Item $transcript -Force
    }
}

Write-Host "Dataset: $env:CHATBOT_DATASET_XLSX"
Write-Host "POST only: simulated_user_message + i-viii user input messages"
Write-Host "Endpoint: https://angel-flight-chatbot-app.azurewebsites.net"
Write-Host ""

& $env:PY (Join-Path (Split-Path $PSScriptRoot -Parent) 'chatbot_live_eval.py')

Write-Host ""
Write-Host "Done. Interim: python score_interim_original_style_short.py" -ForegroundColor Green
