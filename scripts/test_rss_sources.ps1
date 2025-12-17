# Test All RSS Sources
# Проверяет все RSS-источники на работоспособность

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RSS Sources Testing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Import Python module to get sources
$pythonScript = @"
import sys
import os
import json

# Add src to path
project_root = r'$projectRoot'
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from trendoscope2.ingest.news_sources import NewsAggregator

agg = NewsAggregator()

sources = {
    'RUSSIAN_SOURCES': agg.RUSSIAN_SOURCES,
    'RUSSIAN_REGIONAL_SOURCES': agg.RUSSIAN_REGIONAL_SOURCES,
    'RUSSIAN_ECONOMY_SOURCES': agg.RUSSIAN_ECONOMY_SOURCES,
    'RUSSIAN_TECH_SOURCES': agg.RUSSIAN_TECH_SOURCES,
    'RUSSIAN_POLITICS_SOURCES': agg.RUSSIAN_POLITICS_SOURCES,
    'RUSSIAN_CULTURE_SOURCES': agg.RUSSIAN_CULTURE_SOURCES,
    'RUSSIAN_SPORTS_SOURCES': agg.RUSSIAN_SPORTS_SOURCES,
    'EUROPEAN_SOURCES': agg.EUROPEAN_SOURCES,
    'INTERNATIONAL_SOURCES': agg.INTERNATIONAL_SOURCES,
    'INTERNATIONAL_REGIONAL_SOURCES': agg.INTERNATIONAL_REGIONAL_SOURCES,
    'INTERNATIONAL_BUSINESS_SOURCES': agg.INTERNATIONAL_BUSINESS_SOURCES,
    'INTERNATIONAL_TECH_SOURCES': agg.INTERNATIONAL_TECH_SOURCES,
    'AI_SOURCES': agg.AI_SOURCES,
    'POLITICS_SOURCES': agg.POLITICS_SOURCES,
    'US_SOURCES': agg.US_SOURCES,
    'LEGAL_SOURCES': agg.LEGAL_SOURCES,
    'SOCIAL_MEDIA_SOURCES': agg.SOCIAL_MEDIA_SOURCES,
}

import json
print(json.dumps(sources))
"@

# Get all sources from Python
$tempScript = Join-Path $projectRoot "temp_get_sources.py"
$pythonScript | Out-File -FilePath $tempScript -Encoding UTF8

try {
    Push-Location $projectRoot
    
    # Run Python script and capture output
    $pythonOutput = python $tempScript 2>&1
    
    # Separate stdout and stderr
    $stdout = @()
    $stderr = @()
    foreach ($line in $pythonOutput) {
        if ($line -is [System.Management.Automation.ErrorRecord]) {
            $stderr += $line.ToString()
        } else {
            $stdout += $line
        }
    }
    
    if ($stderr.Count -gt 0) {
        Write-Host "Python warnings/errors:" -ForegroundColor Yellow
        $stderr | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        Write-Host ""
    }
    
    # Join stdout lines and parse JSON
    $jsonText = $stdout -join "`n"
    $sources = $jsonText | ConvertFrom-Json
    
    if (-not $sources) {
        throw "Failed to parse sources from JSON"
    }
    
} catch {
    Write-Host "Error getting sources from Python:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    if ($jsonText) {
        Write-Host "JSON output (first 500 chars):" -ForegroundColor Yellow
        Write-Host $jsonText.Substring(0, [Math]::Min(500, $jsonText.Length)) -ForegroundColor Gray
    }
    Pop-Location
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
    exit 1
} finally {
    Pop-Location
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
}

# Function to test RSS URL
function Test-RSSUrl {
    param(
        [string]$Url,
        [int]$Timeout = 10
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url `
            -TimeoutSec $Timeout `
            -UseBasicParsing `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            # Check if it's actually RSS/XML
            $contentType = $response.Headers['Content-Type']
            if ($contentType -like '*xml*' -or $contentType -like '*rss*' -or 
                $response.Content -like '*<?xml*' -or $response.Content -like '*<rss*') {
                return @{
                    Status = "OK"
                    Code = 200
                    Size = $response.Content.Length
                }
            } else {
                return @{
                    Status = "WARNING"
                    Code = 200
                    Message = "Not XML/RSS format"
                }
            }
        } elseif ($response.StatusCode -eq 301 -or $response.StatusCode -eq 302) {
            return @{
                Status = "REDIRECT"
                Code = $response.StatusCode
                Location = $response.Headers['Location']
            }
        } else {
            return @{
                Status = "ERROR"
                Code = $response.StatusCode
            }
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 404) {
            return @{
                Status = "NOT_FOUND"
                Code = 404
            }
        } elseif ($statusCode -eq 403) {
            return @{
                Status = "FORBIDDEN"
                Code = 403
            }
        } elseif ($statusCode -eq 301 -or $statusCode -eq 302) {
            return @{
                Status = "REDIRECT"
                Code = $statusCode
            }
        } else {
            return @{
                Status = "ERROR"
                Code = $statusCode
                Message = $_.Exception.Message
            }
        }
    }
}

# Test all sources
$results = @{
    OK = @()
    REDIRECT = @()
    NOT_FOUND = @()
    FORBIDDEN = @()
    ERROR = @()
    WARNING = @()
}

$totalSources = 0
$testedSources = 0

Write-Host "Testing RSS sources..." -ForegroundColor Cyan
Write-Host ""

foreach ($category in $sources.PSObject.Properties) {
    $categoryName = $category.Name
    $urls = $category.Value
    
    if ($urls.Count -eq 0) {
        continue
    }
    
    Write-Host "Category: $categoryName" -ForegroundColor Yellow
    Write-Host "  Sources: $($urls.Count)" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($url in $urls) {
        $totalSources++
        Write-Host "  Testing: $url" -NoNewline -ForegroundColor Gray
        
        $result = Test-RSSUrl -Url $url -Timeout 10
        
        if ($result.Status -eq "OK") {
            Write-Host " [OK] ($($result.Size) bytes)" -ForegroundColor Green
            $results.OK += @{
                Category = $categoryName
                Url = $url
                Size = $result.Size
            }
            $testedSources++
        } elseif ($result.Status -eq "REDIRECT") {
            Write-Host " [REDIRECT] ($($result.Code))" -ForegroundColor Yellow
            if ($result.Location) {
                Write-Host "    -> $($result.Location)" -ForegroundColor DarkYellow
            }
            $results.REDIRECT += @{
                Category = $categoryName
                Url = $url
                Code = $result.Code
                Location = $result.Location
            }
        } elseif ($result.Status -eq "NOT_FOUND") {
            Write-Host " ✗ 404 NOT FOUND" -ForegroundColor Red
            $results.NOT_FOUND += @{
                Category = $categoryName
                Url = $url
            }
        } elseif ($result.Status -eq "FORBIDDEN") {
            Write-Host " [403 FORBIDDEN]" -ForegroundColor Red
            $results.FORBIDDEN += @{
                Category = $categoryName
                Url = $url
            }
        } elseif ($result.Status -eq "WARNING") {
            Write-Host " [WARNING]: $($result.Message)" -ForegroundColor Yellow
            $results.WARNING += @{
                Category = $categoryName
                Url = $url
                Message = $result.Message
            }
        } else {
            Write-Host " [ERROR] ($($result.Code))" -ForegroundColor Red
            if ($result.Message) {
                Write-Host "    $($result.Message)" -ForegroundColor DarkRed
            }
            $results.ERROR += @{
                Category = $categoryName
                Url = $url
                Code = $result.Code
                Message = $result.Message
            }
        }
        
        Start-Sleep -Milliseconds 200  # Be nice to servers
    }
    
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total sources tested: $totalSources" -ForegroundColor Gray
Write-Host ""
Write-Host "[OK] Working: $($results.OK.Count)" -ForegroundColor Green
Write-Host "[->] Redirects: $($results.REDIRECT.Count)" -ForegroundColor Yellow
Write-Host "[X] Not Found (404): $($results.NOT_FOUND.Count)" -ForegroundColor Red
Write-Host "[X] Forbidden (403): $($results.FORBIDDEN.Count)" -ForegroundColor Red
Write-Host "[!] Warnings: $($results.WARNING.Count)" -ForegroundColor Yellow
Write-Host "[X] Errors: $($results.ERROR.Count)" -ForegroundColor Red
Write-Host ""

# Show problematic sources
if ($results.REDIRECT.Count -gt 0) {
    Write-Host "Redirects (need to fix URLs):" -ForegroundColor Yellow
    foreach ($item in $results.REDIRECT) {
        Write-Host "  $($item.Url)" -ForegroundColor Gray
        if ($item.Location) {
            Write-Host "    -> $($item.Location)" -ForegroundColor DarkYellow
        }
    }
    Write-Host ""
}

if ($results.NOT_FOUND.Count -gt 0) {
    Write-Host "Not Found (404) - Remove from list:" -ForegroundColor Red
    foreach ($item in $results.NOT_FOUND) {
        Write-Host "  $($item.Url) ($($item.Category))" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($results.FORBIDDEN.Count -gt 0) {
    Write-Host "Forbidden (403) - May need authentication:" -ForegroundColor Red
    foreach ($item in $results.FORBIDDEN) {
        Write-Host "  $($item.Url) ($($item.Category))" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($results.ERROR.Count -gt 0) {
    Write-Host "Errors:" -ForegroundColor Red
    foreach ($item in $results.ERROR) {
        Write-Host "  $($item.Url) ($($item.Category))" -ForegroundColor Gray
        if ($item.Message) {
            Write-Host "    $($item.Message)" -ForegroundColor DarkRed
        }
    }
    Write-Host ""
}

# Save results to file
$resultsFile = Join-Path $projectRoot "rss_test_results.json"
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8
Write-Host "Detailed results saved to: $resultsFile" -ForegroundColor Gray
Write-Host ""

# Success rate
$successRate = if ($totalSources -gt 0) {
    [math]::Round(($results.OK.Count / $totalSources) * 100, 1)
} else {
    0
}

$color = if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" }
Write-Host "Success rate: $successRate%" -ForegroundColor $color
Write-Host ""
