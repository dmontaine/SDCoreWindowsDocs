# sdtcl.ps1 - run TCL commands in a real SD session and print what came back.
# This is how the measured listings in the SD TCL document set were produced:
# type the claim as a command, run it, and quote what SD said.
#
# USAGE
#     sdtcl.ps1 -Commands 'list voc sample 3','count voc'
#     sdtcl.ps1 -File commands.txt [-Account don] [-TimeoutSec 90] [-Raw]
#
# WHY IT EXISTS.  sdprobe.ps1 runs a BASIC probe; there was nothing for a TCL
# command, and the TCL pages need their examples run before they are written
# down.
#
# WHY 'don' AND NOT SDSYS, WHICH IS THE SAME REASON sdprobe.ps1 GIVES AND ONE
# MORE.  A user account needs no elevation.  LOGTO SDSYS does: CPROC's
# logto.authorised admits an already-elevated session, an internal one, or one
# that has JUST OBTAINED privilege - and that last route asks UAC, so every run
# against SDSYS puts a consent prompt in front of whoever is at the machine.
# Six runs, six prompts, and the person clicking them is not necessarily the
# person who started the script.  THE GROUP FALLBACK DOES NOT HELP: the SDSYS
# register entry names a group 'sdsys' that does not exist on Windows.
# Measure in a user account unless the thing being measured is SDSYS.
#
# THE SHAPE IS PROJECT_STATUS section 6's: a whole script ending in OFF, fed
# down a pipe under Start-Job with a timeout, with a blank sacrificial first
# line to absorb the pipe's BOM.  A bare "echo CMD | sd" hangs the session and
# leaves a stray sd.exe that costs an elevation to clear.
#
# IT REFUSES A RUN THAT MEASURED NOTHING.  An empty transcript, or fewer
# command echoes than commands sent, and it says so - an empty transcript
# scored against a set of patterns produces tidy negatives that look like
# findings.

[CmdletBinding()]
param(
    [string[]]$Commands,
    [string]$File,
    [string]$Account = 'don',
    [int]$TimeoutSec = 90,
    [switch]$Raw
)

$ErrorActionPreference = 'Stop'

$sdExe = Join-Path $env:ProgramFiles 'SD\usr\bin\sd.exe'

if ($File) {
    if (-not (Test-Path -LiteralPath $File)) { Write-Output "sdtcl: no such file $File"; exit 2 }
    $Commands = @(Get-Content -LiteralPath $File | Where-Object { $_.Trim() -ne '' })
}
if (-not $Commands -or $Commands.Count -eq 0) {
    Write-Output 'sdtcl: no commands given - refusing to run an empty session'
    exit 2
}
if (-not (Test-Path -LiteralPath $sdExe)) { Write-Output "sdtcl: no sd.exe at $sdExe"; exit 2 }

Write-Output '--- sdtcl -----------------------------------------------------'
Write-Output ('  sd.exe  : ' + $sdExe)
Write-Output ('  sha256  : ' + (Get-FileHash -LiteralPath $sdExe -Algorithm SHA256).Hash.Substring(0, 16))
Write-Output ('  account : ' + $Account)
Write-Output ('  commands: ' + $Commands.Count)
foreach ($c in $Commands) { Write-Output ('    | ' + $c) }
Write-Output '---------------------------------------------------------------'

$body = "`n" + ((@("LOGTO $Account", 'TERM 200,9999') + $Commands + @('OFF')) -join "`n") + "`n"

$job = Start-Job -ScriptBlock { param($exe, $text) $text | & $exe } -ArgumentList $sdExe, $body
if (Wait-Job $job -Timeout $TimeoutSec) {
    $out = Receive-Job $job
    $timedOut = $false
} else {
    Stop-Job $job
    $out = Receive-Job $job
    $timedOut = $true
}
Remove-Job $job -Force

# WINDOWS POWERSHELL 5.1 HAS NO `e ESCAPE - it arrived in PowerShell 6, so a
# pattern written "`e\[..." is the literal letter e and strips NOTHING.  This
# is PROJECT_STATUS section 6's trap and it is not theoretical: written that
# way, TERM 200,9999 comes back as TERM<ESC>[7G200,9999 and any check whose
# anchor spans the escape silently misses.  Build it from the code point.
$esc = [string][char]27
$text = (($out -replace ($esc + '\[[0-9;]*[A-Za-z]'), '') -join "`n")

if ($timedOut) {
    Write-Output $text
    Write-Output ''
    Write-Output "*** SD did not finish in $TimeoutSec s - it is waiting for input."
    Write-Output '*** A timed-out session keeps its user-table slot and locks, so'
    Write-Output '*** sdwind will not shut down and cycle.ps1 will refuse to start.'
    Write-Output '*** Stop-Process the sd.exe PID before running anything else.'
    exit 2
}

$echoes = ([regex]::Matches($text, '(?m)^:')).Count
Write-Output ('  transcript lines: ' + (@($text -split "`n")).Count + ', command echoes: ' + $echoes)
if ($text.Trim().Length -eq 0) {
    Write-Output 'sdtcl: THE SESSION PRODUCED NOTHING - refusing to report it as output.'
    exit 2
}
if ($echoes -lt $Commands.Count) {
    Write-Output ('sdtcl: only ' + $echoes + ' command echo(es) for ' + $Commands.Count +
                  ' commands - the session did not get through the script.')
    Write-Output '       The transcript follows so you can see how far it got.'
}

Write-Output ''
if ($Raw) {
    Write-Output $text
} else {
    $keep = @()
    foreach ($l in ($text -split "`n")) {
        $s = $l.TrimEnd("`r")
        if ($s -match '^\s*$') { continue }
        if ($s -match '^:\s*$') { continue }
        $keep += $s
    }
    Write-Output ($keep -join "`n")
}
exit 0
