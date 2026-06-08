$out = 'E:\diagrams'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$files = Get-ChildItem -Path '.\docs\diagrams_mmd' -Filter '*.mmd'
foreach ($f in $files) {
  Write-Output "Rendering $($f.Name) -> $out\$($f.BaseName).svg"
  npx --yes @mermaid-js/mermaid-cli -i $f.FullName -o "$out\$($f.BaseName).svg"
  npx --yes @mermaid-js/mermaid-cli -i $f.FullName -o "$out\$($f.BaseName).png"
}
