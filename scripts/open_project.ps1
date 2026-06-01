<#
.SYNOPSIS
  Open the local Django project in Microsoft Edge.

.DESCRIPTION
  Launches Microsoft Edge in a new window pointed at the local development
  server URL.

.EXAMPLE
  .\scripts\open_project.ps1

.EXAMPLE
  .\scripts\open_project.ps1 -Url 'http://127.0.0.1:8001/'
#>

param(
    [string] $Url = 'http://127.0.0.1:8001/'
)

Set-StrictMode -Version Latest

Start-Process msedge $Url