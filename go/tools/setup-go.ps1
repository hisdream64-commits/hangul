# setup-go.ps1 — 새 PC에서 「한글 교실 고급반」 작업을 이어갈 준비를 마친다.
#
# 쓰는 법 (새 PC 의 PowerShell 에서, 순서대로):
#   1) 공통 준비 — 프로그램 설치와 저장소 받기까지 한 번에:
#        irm https://raw.githubusercontent.com/hisdream64-commits/hangul/main/tools/setup-newpc.ps1 -OutFile setup-newpc.ps1
#        powershell -ExecutionPolicy Bypass -File .\setup-newpc.ps1
#   2) 고급반 몫 — 이 스크립트:
#        powershell -ExecutionPolicy Bypass -File $HOME\projects\hangul\go\tools\setup-go.ps1
#
#   이미 git·python 이 깔려 있고 저장소만 없다면, 2)만 해도 저장소를 받아 옵니다.
#
# 하는 일
#   - 저장소를 받거나 최신으로 맞춘다
#   - 도구가 쓰는 파이썬 패키지(edge-tts 등) 확인
#   - 고급반 전수 점검: 소리 375개가 다 왔는지, 「받아야 할 것 0개」인지
#   - go/MIGRATION.md 를 바탕화면과 Downloads 에 복사
#   - 미리보기 띄우는 법과 Claude 에게 건넬 첫마디를 알려 준다
#
# 옵션:  -NoPull  받지 않고 지금 것 그대로 점검만
#        -NoCopy  문서를 바탕화면에 복사하지 않음
#
# 비밀번호나 키는 어디에도 적지 않습니다.

param([switch]$NoPull, [switch]$NoCopy)

$ErrorActionPreference = 'Stop'
$Repo = 'https://github.com/hisdream64-commits/hangul.git'
$Dest = Join-Path $HOME 'projects\hangul'
$Go   = Join-Path $Dest 'go'

function Say($msg)  { Write-Host ""; Write-Host "== $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "   OK  $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "   !!  $msg" -ForegroundColor Yellow }

Say "1/4  준비물"
foreach ($c in @('git', 'python')) {
    if (-not (Get-Command $c -ErrorAction SilentlyContinue)) {
        Warn "$c 이(가) 없습니다."
        Write-Host "      공통 준비를 먼저 해 주세요 (git·python·Claude 앱까지 깔아 줍니다):" -ForegroundColor Yellow
        Write-Host "        irm https://raw.githubusercontent.com/hisdream64-commits/hangul/main/tools/setup-newpc.ps1 -OutFile setup-newpc.ps1" -ForegroundColor Gray
        Write-Host "        powershell -ExecutionPolicy Bypass -File .\setup-newpc.ps1" -ForegroundColor Gray
        exit 1
    }
    Ok "$c 있음"
}
if (Get-Command node -ErrorAction SilentlyContinue) { Ok "node 있음" }
else { Warn "node 없음 — 소리 목록을 다시 뽑는 점검만 건너뜁니다. 앱과 나머지는 됩니다." }

Say "2/4  저장소"
if (Test-Path (Join-Path $Dest '.git')) {
    if ($NoPull) {
        Ok "이미 있음: $Dest (받지 않음)"
    } else {
        $dirty = (git -C $Dest status --porcelain | Measure-Object -Line).Lines
        if ($dirty -gt 0) {
            Warn "고치던 것이 남아 있어 받지 않았습니다 ($dirty 개). 정리한 뒤 git pull 하세요."
        } else {
            git -C $Dest fetch --all --quiet
            git -C $Dest pull --ff-only --quiet
            Ok "최신으로 받았습니다: $Dest"
        }
    }
} else {
    New-Item -ItemType Directory -Force (Split-Path $Dest) | Out-Null
    git clone --quiet $Repo $Dest
    Ok "받았음: $Dest (기초반 소리 1,226개 + 고급반 375개, 약 29MB)"
}
if (-not (Test-Path $Go)) { Warn "go\ 폴더가 없습니다. 저장소가 옛 판인지 확인해 주세요."; exit 1 }

Say "3/4  파이썬 패키지"
$hasEdge = $false
try { python -c "import edge_tts" 2>$null; $hasEdge = ($LASTEXITCODE -eq 0) } catch { $hasEdge = $false }
if ($hasEdge) {
    Ok "edge-tts 있음 (소리를 다시 만들 수 있습니다)"
} else {
    $req = Join-Path $Dest 'tools\requirements.txt'
    if (Test-Path $req) { python -m pip install --quiet --disable-pip-version-check -r $req }
    else { python -m pip install --quiet --disable-pip-version-check edge-tts }
    Ok "edge-tts 설치됨"
}

Say "4/4  고급반 점검"
$mp3 = @(Get-ChildItem (Join-Path $Go 'audio') -Filter *.mp3 -ErrorAction SilentlyContinue)
# PowerShell 5.1 은 BOM 없는 UTF-8 을 ANSI 로 읽어 한글이 깨집니다. -Encoding UTF8 이 꼭 필요합니다.
$want = (Get-Content (Join-Path $Go 'tools\used.json') -Raw -Encoding UTF8 | ConvertFrom-Json).Count
if ($mp3.Count -eq $want) {
    $mb = [math]::Round(($mp3 | Measure-Object Length -Sum).Sum / 1MB, 1)
    Ok "소리 $($mp3.Count)개 다 있음 ($mb MB)"
} else {
    Warn "소리가 $($mp3.Count)개뿐입니다. 있어야 할 것은 $want 개."
    Write-Host "      python go\tools\make_audio.py  를 돌리면 빠진 것만 받아 옵니다." -ForegroundColor Yellow
}

Push-Location $Dest
# 읽을 말 목록이 앱과 어긋나지 않았는지 (node 가 있을 때만)
if (Get-Command node -ErrorAction SilentlyContinue) {
    $tmp = Join-Path $env:TEMP 'used-check.json'
    cmd /c "node go\tools\extract_used.js go\index.html `"$tmp`" 2>&1" | Out-Null
    if (Test-Path $tmp) {
        $a = (Get-Content $tmp -Raw -Encoding UTF8 | ConvertFrom-Json).Count
        if ($a -eq $want) { Ok "읽을 말 $a 개 — 목록과 앱이 맞습니다" }
        else { Warn "앱에서 뽑은 말은 $a 개인데 목록은 $want 개입니다. go\MIGRATION.md 7절을 보세요." }
        Remove-Item $tmp -Force
    }
}
# 받아야 할 소리가 남아 있는지
$dry = (cmd /c "python go\tools\make_audio.py --dry-run 2>&1" | Out-String)
if ($dry -match '받아야 할 것 0개') { Ok "받아야 할 소리 없음 — 바로 작업하실 수 있습니다" }
else { Warn "점검 결과를 확인해 주세요:"; Write-Host $dry }
Pop-Location

if (-not $NoCopy) {
    $doc = Join-Path $Go 'MIGRATION.md'
    foreach ($d in @([Environment]::GetFolderPath('Desktop'), (Join-Path $HOME 'Downloads'))) {
        if (Test-Path $d) { Copy-Item $doc (Join-Path $d 'MIGRATION-고급반.md') -Force; Ok (Join-Path $d 'MIGRATION-고급반.md') }
    }
}

Write-Host ""
Write-Host "준비 끝. 이어서 할 일:" -ForegroundColor Cyan
Write-Host "  1) 시작 메뉴에서 Claude 앱을 열고 같은 계정으로 로그인"
Write-Host "  2) Code 탭 → 폴더 선택 → $Dest"
Write-Host "  3) 첫마디로 이렇게 말하세요:" -ForegroundColor Gray
Write-Host '     "go/MIGRATION.md 를 읽고 한글 교실 고급반 작업을 이어서 해줘."' -ForegroundColor Yellow
Write-Host ""
Write-Host "  화면을 보려면:  cd $Go ; python -m http.server 8000"
Write-Host "    그 뒤 브라우저에서  http://localhost:8000/index.html"
Write-Host "    🔊 를 눌러 성우 목소리가 나오면 제대로 온 것입니다."
Write-Host ""
Write-Host "  ※ 제 12 과 「소리 내어 읽기」의 녹음은 http://localhost 또는 https 에서만 됩니다." -ForegroundColor Gray
Write-Host "     파일을 더블클릭해 여는 file:// 방식으로는 마이크가 열리지 않습니다." -ForegroundColor Gray
