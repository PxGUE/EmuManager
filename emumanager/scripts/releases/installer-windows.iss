#define MyAppName "EmuManager"
#define MyAppVersion "0.5.0"
#define MyAppPublisher "PxGUE"
#define MyAppURL "https://github.com/PxGUE/EmuManager"
#define MyAppExeName "EmuManager.exe"
#define MyIconPath "..\..\ui\assets\logo.ico"
#define MySourcePath "..\..\..\release\Windows\Standalone\*"

[Setup]
AppId={{B51FC9A0-5E4D-4DBA-9DE9-7AD855D192FC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={commonpf64}\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=..\..\..\release\Windows
OutputBaseFilename=EmuManager-v{#MyAppVersion}-Setup
SetupIconFile={#MyIconPath}
Compression=lzma
SolidCompression=yes

; --- MEJORAS VISUALES ---
WizardStyle=modern
WizardResizable=yes
; Rutas de imágenes de marca
WizardImageFile=..\..\ui\assets\installer_side.bmp
WizardSmallImageFile=..\..\ui\assets\installer_logo.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MySourcePath}"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Messages]
spanish.WelcomeLabel1=Bienvenido al instalador de {#MyAppName}
spanish.WelcomeLabel2=Este asistente instalará la versión más potente de tu gestor de retro-gaming.

[Code]
// Helper para escanear procesos activos (Debe ir primero en Pascal)
function IsAppRunning(const FileName: string): Boolean;
var
  FSWbemLocator: Variant;
  FWMIService: Variant;
  FWbemObjectSet: Variant;
begin
  Result := False;
  try
    FSWbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('', 'root\CIMV2');
    FWbemObjectSet := FWMIService.ExecQuery(Format('SELECT * FROM Win32_Process WHERE Name="%s"', [FileName]));
    Result := (FWbemObjectSet.Count > 0);
  except
  end;
end;

// Función para detectar si la app está abierta y cerrarla
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  while IsAppRunning('{#MyAppExeName}') do
  begin
    if MsgBox('{#MyAppName} se está ejecutando actualmente.' #13#10 #13#10 +
              'Por favor, cierra la aplicación antes de continuar o pulsa "Sí" para intentar cerrarla automáticamente.', 
              mbError, MB_YESNO) = idYes then
    begin
      ShellExec('open', 'taskkill.exe', '/f /im {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
      Sleep(1000);
    end
    else
    begin
      Result := False;
      Break;
    end;
  end;
end;
