; Script de Inno Setup para EmuManager
; Genera un instalador profesional para Windows

#define MyAppName "EmuManager"
#define MyAppVersion "0.1.13-alpha"
#define MyAppPublisher "PxGUE"
#define MyAppURL "https://github.com/PxGUE/EmuManager"
#define MyAppExeName "emumanager.exe"

[Setup]
; AppId único para este instalador (generado aleatoriamente para el proyecto)
AppId={{B2A9E5F1-7C2D-4C9E-9A1B-9E1A2B3D4E5F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Carpeta donde se guardará el instalador final
OutputDir=..\installer
OutputBaseFilename=EmuManager_v{#MyAppVersion}_Setup
; Icono del instalador (usamos el logo si existe en formato ico, si no omitir)
SetupIconFile=..\media\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivos compilados por Nuitka (standalone)
Source: "build_output\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTA: Asegúrate de que emumanager.exe esté en esa carpeta

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
