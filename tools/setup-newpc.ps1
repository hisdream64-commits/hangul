# setup-newpc.ps1 — 새 PC에서 「우리 한글 교실」 작업을 이어갈 준비를 한 번에 한다.
#
# 쓰는 법 (새 PC의 PowerShell 에서, 순서대로):
#   1) 이 파일을 받는다 (브라우저에서 저장하거나):
#        irm https://raw.githubusercontent.com/hisdream64-commits/hangul/main/tools/setup-newpc.ps1 -OutFile setup-newpc.ps1
#   2) 내용을 한 번 훑어본 뒤 실행한다:
#        powershell -ExecutionPolicy Bypass -File .\setup-newpc.ps1
#
# 하는 일
#   - git, GitHub CLI(gh), Python 이 없으면 winget 으로 설치
#   - 저장소를 $HOME\projects\hangul 에 받는다 (이미 있으면 최신으로)
#   - 이 저장소의 커밋 작성자를 hisdream64-commits 로
#   - 도구가 쓰는 파이썬 패키지 설치
#   - gh 가 hisdream64-commits 로 로그인되어 있지 않으면 로그인 절차 시작 (브라우저 승인 필요)
#   - 인수인계 문서를 바탕화면과 다운로드 폴더에 복사
#
# 비밀번호나 키는 어디에도 적지 않습니다. gh 로그인은 브라우저에서 직접 승인합니다.

$ErrorActionPreference = 'Stop'
$Repo    = 'https://github.com/hisdream64-commits/hangul.git'
$Dest    = Join-Path $HOME 'projects\hangul'
$GitUser = 'hisdream64-commits'
$GitMail = 'hisdream64@gmail.com'

function Say($msg)  { Write-Host ""; Write-Host "== $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "   OK  $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "   !!  $msg" -ForegroundColor Yellow }

function Need($cmd, $wingetId, $label) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { Ok "$label 있음"; return }
    Warn "$label 없음 → winget 으로 설치합니다"
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "winget 이 없습니다. Microsoft Store 에서 '앱 설치 관리자'를 설치한 뒤 다시 실행해 주세요."
    }
    winget install --id $wingetId -e --accept-source-agreements --accept-package-agreements
    # 방금 설치한 것이 이 창에서 보이도록 PATH 를 다시 읽는다
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "$label 설치는 됐지만 이 창에서 아직 안 보입니다. PowerShell 을 닫았다 다시 열고 한 번 더 실행해 주세요."
    }
    Ok "$label 설치됨"
}

Say "1/6  필요한 프로그램"
Need git    'Git.Git'            'git'
Need gh     'GitHub.cli'         'GitHub CLI (gh)'
Need python 'Python.Python.3.13' 'Python'
if (Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") { Ok "Chrome 있음" }
else { Warn "Chrome 없음 — 안내문 PDF(regen_qr_poster.py)를 만들 때만 필요합니다. 나머지는 됩니다." }

Say "2/6  저장소"
if (Test-Path (Join-Path $Dest '.git')) {
    Ok "이미 있음: $Dest → 최신으로 받습니다"
    git -C $Dest fetch --all --quiet
    git -C $Dest pull --ff-only --quiet
} else {
    New-Item -ItemType Directory -Force (Split-Path $Dest) | Out-Null
    git clone --quiet $Repo $Dest
    Ok "받았음: $Dest (소리 1,226개 포함, 약 21MB)"
}

Say "3/6  이 저장소의 커밋 작성자"
git -C $Dest config user.name  $GitUser
git -C $Dest config user.email $GitMail
Ok "$GitUser <$GitMail> (이 저장소 안에서만)"

Say "4/6  도구가 쓰는 파이썬 패키지"
python -m pip install --quiet --disable-pip-version-check -r (Join-Path $Dest 'tools\requirements.txt')
Ok "tools/requirements.txt 충족"

Say "5/6  GitHub 로그인"
# gh 는 상태를 stderr 로 찍는다. PowerShell 5.1 은 이를 오류로 바꿔 멈추므로 cmd 를 거쳐 받는다.
$active = (cmd /c "gh auth status 2>&1" | Out-String)
if ($active -match "account $GitUser" -and $active -match "(?s)$GitUser.*?Active account: true") {
    Ok "$GitUser 로 로그인되어 있음"
} elseif ($active -match "account $GitUser") {
    gh auth switch --user $GitUser
    Ok "$GitUser 로 바꿨음"
} else {
    Warn "$GitUser 로 로그인되어 있지 않습니다. 지금 로그인 절차를 시작합니다."
    Write-Host "      화면에 8자리 코드가 나오면 브라우저에서 $GitUser 계정으로 승인해 주세요." -ForegroundColor Yellow
    gh auth login --web --git-protocol https --hostname github.com
}

Say "6/6  인수인계 문서 복사"
$doc = Join-Path $Dest 'docs\MIGRATION.md'
foreach ($d in @([Environment]::GetFolderPath('Desktop'), (Join-Path $HOME 'Downloads'))) {
    if (Test-Path $d) { Copy-Item $doc (Join-Path $d 'MIGRATION.md') -Force; Ok (Join-Path $d 'MIGRATION.md') }
}

Say "확인"
Push-Location $Dest
python tools\clips.py | Select-Object -First 1
$branches = git branch -r --format='%(refname:short)' | Where-Object { $_ -ne 'origin/HEAD' }
Pop-Location
Ok ("가지: " + ($branches -join ', '))

Write-Host ""
Write-Host "준비 끝. 이어서 할 일:" -ForegroundColor Cyan
Write-Host "  cd $Dest"
Write-Host "  git switch wip/voice-guide        # 하던 작업(①②④⑥) 가지"
Write-Host "  docs\MIGRATION.md 의 0-1절을 읽거나, Claude 에게 이렇게 말하세요:"
Write-Host '  "docs/MIGRATION.md 0-1절을 읽고, wip/voice-guide 가지에서 남은 일을 이어서 해줘."'
