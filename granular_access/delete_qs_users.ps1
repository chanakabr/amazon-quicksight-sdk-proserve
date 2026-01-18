# Script to delete all QuickSight users
$env:AWS_PROFILE="442091038412"
$accountId = "442091038412"
$region = "us-east-1"
$namespace = "default"

# List of users to delete (excluding the admin account 442091038412)
$users = @(
    "quicksight-fed-us-users/JoyceKemp@oktank.com",
    "quicksight-fed-us-users/JohnKing@oktank.com",
    "quicksight-fed-us-users/TeresitaRedd@oktank.com",
    "quicksight-fed-us-users/GretchenJoyce@oktank.com",
    "quicksight-fed-us-users/AlbertPowers@oktank.com",
    "quicksight-fed-us-users/KevinGunn@oktank.com",
    "quicksight-fed-us-users/MichaelBrown@oktank.com",
    "quicksight-fed-us-users/TimothyMcgloin@oktank.com",
    "quicksight-fed-us-users/WayneMaxwell@oktank.com",
    "quicksight-fed-us-users/ThomasYang@oktank.com",
    "quicksight-fed-us-users/TrinhHartmann@oktank.com",
    "quicksight-fed-us-users/StephenMoretz@oktank.com",
    "quicksight-fed-us-users/CatherineCimino@oktank.com",
    "quicksight-fed-us-users/StevenLudwick@oktank.com",
    "quicksight-fed-us-users/MarshallBanks@oktank.com",
    "quicksight-fed-us-users/BettyRamirez@oktank.com"
)

Write-Host "Starting QuickSight user deletion..." -ForegroundColor Cyan
Write-Host "Total users to delete: $($users.Count)" -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($user in $users) {
    Write-Host "Deleting user: $user" -ForegroundColor White
    
    try {
        aws quicksight delete-user `
            --aws-account-id $accountId `
            --namespace $namespace `
            --user-name $user `
            --region $region 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Successfully deleted $user" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ✗ Failed to delete $user" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "  ✗ Error deleting $user : $_" -ForegroundColor Red
        $failCount++
    }
    
    Start-Sleep -Milliseconds 500  # Brief pause between deletions
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deletion Summary:" -ForegroundColor Cyan
Write-Host "  Successful: $successCount" -ForegroundColor Green
Write-Host "  Failed: $failCount" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan

# Optionally delete the admin user (commented out for safety)
Write-Host ""
Write-Host "Note: Admin user 442091038412 was NOT deleted (you can delete manually if needed)" -ForegroundColor Yellow
