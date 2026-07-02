$ProjectDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$VbsPath     = Join-Path $ProjectDir "launch.vbs"
$IconPath    = Join-Path $ProjectDir "app_icon.ico"
$Desktop     = [System.Environment]::GetFolderPath("Desktop")
$Shortcut    = Join-Path $Desktop "AI_Research_Team.lnk"

# app_icon.ico가 없으면 Python으로 먼저 생성
if (-not (Test-Path $IconPath)) {
    $GenScript = @'
import os, struct, math
SIZE = 32; cx = cy = SIZE / 2 - 0.5
BLURP=bytes([0xf2,0x65,0x58,0xff]); WHITE=bytes([0xff,0xff,0xff,0xff])
MAGENT=bytes([0xbd,0x48,0xec,0xff]); TRANSP=bytes([0x00,0x00,0x00,0x00])
img=[[TRANSP]*SIZE for _ in range(SIZE)]
for y in range(SIZE):
 for x in range(SIZE):
  if (x-cx)**2+(y-cy)**2<=14.5**2: img[y][x]=BLURP
for ad in [0,60,120]:
 ar=math.radians(ad); ca,sa=math.cos(ar),math.sin(ar)
 for t in range(720):
  tr=math.radians(t/2); lx=12*math.cos(tr); ly=4*math.sin(tr)
  gx=lx*ca-ly*sa+cx; gy=lx*sa+ly*ca+cy
  for dx,dy in [(0,0),(1,0),(0,1)]:
   px,py=int(gx)+dx,int(gy)+dy
   if 0<=px<SIZE and 0<=py<SIZE: img[py][px]=WHITE
for y in range(SIZE):
 for x in range(SIZE):
  if (x-cx)**2+(y-cy)**2<=3.5**2: img[y][x]=MAGENT
pix=b''.join(img[y][x] for y in range(SIZE-1,-1,-1) for x in range(SIZE))
rb=((SIZE+31)//32)*4; am=b'\x00'*(rb*SIZE)
bih=struct.pack('<IiiHHIIiiII',40,SIZE,SIZE*2,1,32,0,0,0,0,0,0)
idata=bih+pix+am
ico=struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',SIZE,SIZE,0,0,1,32,len(idata),22)+idata
open(r'__ICON_PATH__','wb').write(ico)
'@ -replace '__ICON_PATH__', $IconPath.Replace('\','\\')
    python -c $GenScript
}

$Shell = New-Object -ComObject WScript.Shell
$Link  = $Shell.CreateShortcut($Shortcut)
$Link.TargetPath       = "wscript.exe"
$Link.Arguments        = "`"$VbsPath`""
$Link.WorkingDirectory = $ProjectDir
$Link.Description      = "AI 연구 토론팀 - 연구 아이디어 분석"
if (Test-Path $IconPath) { $Link.IconLocation = "$IconPath,0" }
$Link.Save()

Write-Host ""
Write-Host "바탕화면에 'AI 연구 토론팀' 단축키가 생성되었습니다!" -ForegroundColor Green
Write-Host "이제 바탕화면 아이콘을 더블클릭하면 앱이 열립니다." -ForegroundColor Cyan
Write-Host ""
