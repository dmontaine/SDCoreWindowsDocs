<#
    release.ps1 - render what has changed, prove nothing is stale, and zip the
    deliverable with a checksum.

    command line:
        tools\release.ps1 [-Set Testing] [-Version W1.0-0] [-OutDir <dir>]
                          [-Force] [-NoZip]

    WHY THIS EXISTS, and it is not the ten minutes it saves.  Moving the
    documentation into its own repository gave up the only automatic check
    that a page still matched the product (assert-current never sees it now).
    Zipping by hand adds a SECOND way to drift: shipping a PDF that was
    rendered before the last Markdown fix.  Nothing would catch it, and it
    looks exactly like a correct release.  So the staleness test below is the
    point of the script and the zip is the convenience.

    WHAT IT RENDERS.  Only what changed - owner's ruling, 26 Aug 2026,
    question 16.  A page is rendered when its .html or .pdf is missing or
    older than the .md beside it.  -Force renders everything.

    IT REFUSES RATHER THAN SHIPPING A DOUBT.  No .md found, a generated file
    with no source, or any .pdf still older than its .md after the render, and
    it stops with a non-zero exit.  A release step that passes because it did
    nothing is the failure this is shaped to avoid.
#>

[CmdletBinding()]
param(
    [string]$Set     = 'Testing',
    [string]$Version = 'W1.0-0',
    [string]$OutDir,
    [switch]$Force,
    [switch]$NoZip
)

$ErrorActionPreference = 'Stop'

function Say($m) { Write-Output ("release: " + $m) }

# --- resolve everything, and say what was resolved -------------------------
$tools = $PSScriptRoot
$root  = Split-Path -Parent $tools
$setDir = Join-Path $root $Set
$mdDir   = Join-Path $setDir 'markdown'
$htmlDir = Join-Path $setDir 'html'
$pdfDir  = Join-Path $setDir 'pdf'
if (-not $OutDir) { $OutDir = $root }

Say ("repository  " + $root)
Say ("set         " + $Set + "   version " + $Version)
Say ("markdown    " + $mdDir)
Say ("html        " + $htmlDir)
Say ("pdf         " + $pdfDir)

foreach ($d in @($mdDir, $htmlDir, $pdfDir)) {
    if (-not (Test-Path -LiteralPath $d)) {
        Write-Error ("no such directory: " + $d)
    }
}

$sources = @(Get-ChildItem -LiteralPath $mdDir -Filter '*.md' | Sort-Object Name)
Say ("sources     " + $sources.Count + " markdown page(s)")
if ($sources.Count -eq 0) {
    Write-Error "no .md files - refusing to report a release"
}

# --- a generated file with no source is a renumbering left half-done -------
$stems = @($sources | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_.Name) })
$orphans = @()
$generated = @(Get-ChildItem -LiteralPath $htmlDir -Filter '*.html') +
             @(Get-ChildItem -LiteralPath $pdfDir  -Filter '*.pdf')
foreach ($g in $generated) {
    $stem = [IO.Path]::GetFileNameWithoutExtension($g.Name)
    if ($stems -notcontains $stem) { $orphans += $g.FullName }
}
if ($orphans.Count -gt 0) {
    Say "GENERATED FILES WITH NO MARKDOWN SOURCE:"
    $orphans | ForEach-Object { Say ("    " + $_) }
    Write-Error ("" + $orphans.Count + " orphan(s) - delete them or restore the source, then run again")
}

# --- what needs rendering --------------------------------------------------
function Needs($generated, $source) {
    if (-not (Test-Path -LiteralPath $generated)) { return $true }
    return ((Get-Item -LiteralPath $generated).LastWriteTimeUtc -lt $source.LastWriteTimeUtc)
}

$toHtml = @()
foreach ($s in $sources) {
    $stem = [IO.Path]::GetFileNameWithoutExtension($s.Name)
    if ($Force -or (Needs (Join-Path $htmlDir ($stem + '.html')) $s)) { $toHtml += $s }
}

Say ("to render   " + $toHtml.Count + " of " + $sources.Count + " page(s) to HTML" +
     $(if ($Force) { "   (-Force)" } else { "" }))

if ($toHtml.Count -gt 0) {
    # A native exe writing to stderr terminates the script under
    # ErrorActionPreference Stop, so the exit code is read explicitly.
    # NOT $args.  That is a PowerShell automatic variable: naming a parameter
    # or a local $args gets it clobbered, and the command runs with nothing
    # after it.  This project has paid for that once already.
    $mkdoc = Join-Path $tools 'mkdoc.py'
    $mkdocArgs = @('--in') + @($toHtml | ForEach-Object { $_.FullName }) +
                 @('--out', $htmlDir, '--product', 'SD Core for Windows',
                   '--version', $Version)
    Say ("python " + $mkdoc + " " + ($mkdocArgs -join ' '))
    if ($mkdocArgs.Count -lt 5) { Write-Error 'mkdoc argument list is too short to be right' }
    & python $mkdoc @mkdocArgs 2>&1 | ForEach-Object { Write-Output ("  " + $_) }
    if ($LASTEXITCODE -ne 0) { Write-Error ("mkdoc.py exited " + $LASTEXITCODE) }
}

$toPdf = @()
foreach ($s in $sources) {
    $stem = [IO.Path]::GetFileNameWithoutExtension($s.Name)
    $html = Join-Path $htmlDir ($stem + '.html')
    if (-not (Test-Path -LiteralPath $html)) { Write-Error ("no HTML for " + $s.Name) }
    if ($Force -or (Needs (Join-Path $pdfDir ($stem + '.pdf')) (Get-Item -LiteralPath $html))) {
        $toPdf += $html
    }
}

Say ("to print    " + $toPdf.Count + " of " + $sources.Count + " page(s) to PDF")

foreach ($html in $toPdf) {
    & (Join-Path $tools 'mkpdf.ps1') -In $html -Out $pdfDir | ForEach-Object { Write-Output ("  " + $_) }
}

# --- THE CHECK THIS SCRIPT EXISTS FOR --------------------------------------
# Every deliverable must be newer than the source it was made from.  This runs
# whether or not anything was rendered, so a run that rendered nothing still
# has to prove the set is current.
$stale = @()
foreach ($s in $sources) {
    $stem = [IO.Path]::GetFileNameWithoutExtension($s.Name)
    foreach ($ext in @('html', 'pdf')) {
        $g = Join-Path (Join-Path $setDir $ext) ($stem + '.' + $ext)
        if (-not (Test-Path -LiteralPath $g)) { $stale += ($stem + '.' + $ext + '  MISSING'); continue }
        $gi = Get-Item -LiteralPath $g
        if ($gi.LastWriteTimeUtc -lt $s.LastWriteTimeUtc) {
            $stale += ($stem + '.' + $ext + '  ' + $gi.LastWriteTimeUtc.ToString('s') +
                       '  older than  ' + $s.LastWriteTimeUtc.ToString('s'))
        }
    }
}

if ($stale.Count -gt 0) {
    Say "STALE OR MISSING DELIVERABLES:"
    $stale | ForEach-Object { Say ("    " + $_) }
    Write-Error ("" + $stale.Count + " stale - the zip was NOT written")
}
Say ("current     all " + $sources.Count + " page(s): html and pdf both newer than their markdown")

if ($NoZip) { Say 'no zip written (-NoZip)'; exit 0 }

# --- the deliverable -------------------------------------------------------
$zip = Join-Path $OutDir ("SD-Core-for-Windows-" + $Version + "-" + $Set + "-docs.zip")
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }

Compress-Archive -Path @($pdfDir, $htmlDir) -DestinationPath $zip
$item = Get-Item -LiteralPath $zip
$sha  = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash

Say ("zip         " + $item.FullName)
Say ("size        " + $item.Length + " bytes")
Say ("sha256      " + $sha)
Say ("contents    " + $sources.Count + " page(s), html and pdf")
exit 0
