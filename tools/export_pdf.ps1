$base = (Get-Location).Path
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
    $chrome = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}

$files = @(
    @{
        In = Join-Path $base "output\Bien_Ban_Hop_Review_Nghiem_Thu_He_Thong_AMIS_TFLEX_Nido_28-11-2026.html"
        Out = Join-Path $base "output\Bien_Ban_Hop_Review_Nghiem_Thu_He_Thong_AMIS_TFLEX_Nido_28-11-2026.pdf"
        Sync = Join-Path $base "doc\transcripts\Bien_Ban_Hop_Review_Nghiem_Thu_He_Thong_AMIS_TFLEX_Nido_28-11-2026.pdf"
    },
    @{
        In = Join-Path $base "output\Bien_Ban_Hop_Review_Nghiem_Thu_AMIS_TFLEX_Nido_Rut_Gon.html"
        Out = Join-Path $base "output\Bien_Ban_Hop_Review_Nghiem_Thu_AMIS_TFLEX_Nido_Rut_Gon.pdf"
        Sync = Join-Path $base "doc\transcripts\Bien_Ban_Hop_Review_Nghiem_Thu_AMIS_TFLEX_Nido_Rut_Gon.pdf"
    }
)

foreach ($f in $files) {
    Write-Host "Rendering $($f.In) -> $($f.Out)..."
    $argList = "--headless --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=`"$($f.Out)`" `"$($f.In)`""
    Write-Host "Running: $chrome $argList"
    $p = Start-Process -FilePath $chrome -ArgumentList $argList -Wait -PassThru -NoNewWindow
    Write-Host "ExitCode: $($p.ExitCode)"
    if (Test-Path $f.Out) {
        Copy-Item $f.Out $f.Sync -Force
        $item = Get-Item $f.Out
        Write-Host "SUCCESS: $($item.FullName) ($($item.Length) bytes)"
    } else {
        Write-Host "FAILED: $($f.Out)"
    }
}
