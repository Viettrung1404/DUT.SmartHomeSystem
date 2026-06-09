$ErrorActionPreference = "Stop"

$preferredAlias = "Wi-Fi"
$ipAddress = $env:EXPO_LAN_IP

if (-not $ipAddress) {
    $ipAddress = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object {
            $_.InterfaceAlias -eq $preferredAlias -and
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*"
        } |
        Select-Object -First 1 -ExpandProperty IPAddress
}

if (-not $ipAddress) {
    $ipAddress = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.PrefixOrigin -ne "WellKnown"
        } |
        Select-Object -First 1 -ExpandProperty IPAddress
}

if (-not $ipAddress) {
    throw "Cannot find a LAN IPv4 address. Set EXPO_LAN_IP manually, for example: `$env:EXPO_LAN_IP='10.10.59.240'"
}

$env:REACT_NATIVE_PACKAGER_HOSTNAME = $ipAddress
$env:EXPO_PUBLIC_API_URL = "http://${ipAddress}:8000"

Write-Host "Development build mode"
Write-Host "Expo LAN IP: $ipAddress"
Write-Host "Backend URL: $env:EXPO_PUBLIC_API_URL"
Write-Host "Phone test: open http://${ipAddress}:8081/status and expect packager-status:running"
Write-Host "Open the installed development build app, not Expo Go."
Write-Host ""

npx expo start --dev-client --lan -c
