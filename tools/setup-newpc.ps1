# setup-newpc.ps1 — 새 PC에서 「우리 한글 교실」 작업을 이어갈 준비를 한 번에 한다.
#
# 쓰는 법 (새 PC의 PowerShell 에서, 순서대로):
#   1) 이 파일을 받는다 (브라우저에서 저장하거나):
#        irm https://raw.githubusercontent.com/hisdream64-commits/hangul/main/tools/setup-newpc.ps1 -OutFile setup-newpc.ps1
#   2) 내용을 한 번 훑어본 뒤 실행한다:
#        powershell -ExecutionPolicy Bypass -File .\setup-newpc.ps1
#
# 하는 일
#   - git, GitHub CLI(gh), Python, Claude 데스크톱 앱이 없으면 winget 으로 설치
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
# Node 는 받아쓰기 중급반(jung.html / gyeopbatchim.html)을 다시 만들 때만 씁니다.
# 기초반만 손보실 거면 없어도 됩니다.
Need node   'OpenJS.NodeJS.LTS'  'Node.js (받아쓰기 중급반 빌드용)'
if (Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") { Ok "Chrome 있음" }
else { Warn "Chrome 없음 — 안내문 PDF(regen_qr_poster.py)를 만들 때만 필요합니다. 나머지는 됩니다." }

# Claude 데스크톱 앱 — 새 PC에서 Claude 가 직접 손을 쓰려면 이것이 있어야 한다.
# (크롬 확장으로는 브라우저만 다룰 수 있고, 프로그램 설치나 저장소 작업은 못 한다)
$claudeListed = (cmd /c "winget list --id Anthropic.Claude -e --accept-source-agreements 2>&1" | Out-String)
if ($claudeListed -match 'Anthropic\.Claude') { Ok "Claude 앱 있음" }
else {
    Warn "Claude 앱 없음 → winget 으로 설치합니다"
    winget install --id Anthropic.Claude -e --accept-source-agreements --accept-package-agreements
    Ok "Claude 앱 설치됨 — 끝나면 시작 메뉴에서 Claude 를 열고 같은 계정으로 로그인하세요"
}

Say "2/6  저장소"
if (Test-Path (Join-Path $Dest '.git')) {
    Ok "이미 있음: $Dest → 최신으로 받습니다"
    # git 은 진행 상태를 stderr 로 찍는다. PowerShell 5.1 은 이를 오류로 바꿔 멈추므로 cmd 를 거친다.
    cmd /c "git -C ""$Dest"" fetch --all --quiet 2>&1" | Out-Null
    # 가지를 옮겨 둔 채였거나 안 올린 커밋이 있으면 pull 이 멈춥니다. 그때는 건드리지 않습니다.
    $pull = (cmd /c "git -C ""$Dest"" pull --ff-only --quiet 2>&1" | Out-String)
    if ($LASTEXITCODE -ne 0) {
        $cur = (cmd /c "git -C ""$Dest"" rev-parse --abbrev-ref HEAD 2>&1" | Out-String).Trim()
        Warn "지금 가지($cur)를 그대로 둡니다 — 안 올린 커밋이 있거나 다른 가지에 계신 듯합니다"
        if ($pull.Trim()) { Write-Host ("      " + $pull.Trim()) -ForegroundColor DarkGray }
    }
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
foreach ($name in @('MIGRATION.md', 'DICTATION.md')) {
    $doc = Join-Path $Dest "docs\$name"
    if (-not (Test-Path $doc)) { continue }
    foreach ($d in @([Environment]::GetFolderPath('Desktop'), (Join-Path $HOME 'Downloads'))) {
        if (Test-Path $d) { Copy-Item $doc (Join-Path $d $name) -Force; Ok (Join-Path $d $name) }
    }
}

Say "확인"
Push-Location $Dest
python tools\clips.py | Select-Object -First 1
$branches = git branch -r --format='%(refname:short)' | Where-Object { $_ -ne 'origin/HEAD' }

# 받아쓰기 중급반의 오프라인 소리와 기초반 메뉴 연결은 아직 가지에 있습니다.
# main 만 받으면 그 부분이 없는 옛 화면이 옵니다.
$cur = (cmd /c "git rev-parse --abbrev-ref HEAD 2>&1" | Out-String).Trim()
if ($branches -contains 'origin/wip/dictation-offline' -and $cur -ne 'wip/dictation-offline') {
    Warn "중급반 오프라인 소리·메뉴 연결은 가지 wip/dictation-offline 에 있습니다 (지금 가지: $cur)"
    Write-Host "      그쪽에서 이어가시려면:  git switch wip/dictation-offline" -ForegroundColor Yellow
}

# 받아쓰기 중급반 — 파일이 다 왔는지, 다시 만들 수 있는 상태인지
$dict = @('jung.html', 'gyeopbatchim.html', 'tools\dictation\build.js') |
        Where-Object { -not (Test-Path (Join-Path $Dest $_)) }
if ($dict) { Warn ("받아쓰기 중급반 파일 없음: " + ($dict -join ', ')) }
else {
    Ok "받아쓰기 중급반 파일 있음 (jung.html, gyeopbatchim.html)"
    if (Get-Command node -ErrorAction SilentlyContinue) {
        Push-Location (Join-Path $Dest 'tools\dictation')
        $out = (cmd /c "node build.js ..\..\index.html 2>&1" | Out-String)
        Pop-Location
        if ($out -match '녹음이 필요한 낱말 0 개') {
            Move-Item (Join-Path $Dest 'tools\dictation\jung.html')         $Dest -Force
            Move-Item (Join-Path $Dest 'tools\dictation\gyeopbatchim.html') $Dest -Force
            Ok "받아쓰기 중급반 다시 만들기 됨"
        } else {
            Warn "받아쓰기 중급반 빌드가 깨끗하지 않습니다. docs/DICTATION.md 3절을 보세요."
            Write-Host $out
        }
    } else { Warn "Node 가 없어 중급반 빌드는 건너뜁니다 (화면은 그대로 동작합니다)" }
}
Pop-Location
Ok ("가지: " + ($branches -join ', '))

Write-Host ""
Write-Host "준비 끝. 이어서 할 일:" -ForegroundColor Cyan
Write-Host "  1) 시작 메뉴에서 Claude 앱을 열고 같은 계정으로 로그인"
Write-Host "  2) Code 탭 → 폴더 선택 → $Dest"
Write-Host "  3) 첫마디로 이렇게 말하세요:"
Write-Host "     - 기초반을 이어서:" -ForegroundColor Gray
Write-Host '       "wip/voice-guide 가지에서 기초반 소리 안내를 이어서 해줘."' -ForegroundColor Yellow
Write-Host "     - 받아쓰기 중급반을 이어서:" -ForegroundColor Gray
Write-Host '       "wip/dictation-offline 가지에서 받아쓰기 중급반을 이어서 해줘."' -ForegroundColor Yellow
Write-Host ""
Write-Host "     저장소에 CLAUDE.md 가 있어 규칙과 읽을 문서는 Claude 가 알아서 봅니다." -ForegroundColor Gray
Write-Host "     (소리를 가공하지 말 것 - 고친 뒤 stamp_sw.py - 커밋은 경로 지정)" -ForegroundColor Gray
Write-Host ""
Write-Host "  소리가 나는지 보려면:  cd $Dest ; python -m http.server 8000"
Write-Host "    그 뒤 브라우저에서  http://localhost:8000/jung.html  → 🔊 를 눌러 보세요"
Write-Host ""
Write-Host "  비행기 모드에서도 소리가 나는지 (중급반):" -ForegroundColor Gray
Write-Host "    pip install playwright ; python -m playwright install chromium   (처음 한 번)"
Write-Host "    python tools\dictation\check_offline.py"
Write-Host ""
Write-Host "  (가지를 직접 옮기시려면)" -ForegroundColor Gray
Write-Host "    cd $Dest ; git switch wip/voice-guide          # 기초반 소리 안내"
Write-Host "    cd $Dest ; git switch wip/dictation-offline    # 중급반 오프라인 소리·메뉴"
