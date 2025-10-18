#NoEnv
#SingleInstance Off
SetBatchLines, -1
SendMode, Input
SetTitleMatchMode, 2
DetectHiddenWindows, On
SetKeyDelay, 50, 30
SetMouseDelay, 30

if (A_Args.Length() < 1) {
    MsgBox, 16, Agent3 Error, Missing INI path. Usage: AutoHotkey.exe agent3.ahk "path\agent3_payload.ini"
    ExitApp
}
ini := A_Args[1]

IniRead, TargetTitle, %ini%, General, window_title, WinXP for VB6
IniRead, name,    %ini%, Data, name
IniRead, address, %ini%, Data, address
IniRead, dob,     %ini%, Data, date_of_birth
IniRead, age,     %ini%, Data, age
IniRead, sex,     %ini%, Data, sex

GetCoord(ByRef outx, ByRef outy, key) {
    global ini
    IniRead, raw, %ini%, Coords, %key%
    if (ErrorLevel || raw = "") {
        MsgBox, 16, Agent3 Error, Missing coordinate for %key%.
        ExitApp
    }
    StringSplit, parts, raw, `,
    outx := parts1
    outy := parts2
}

GetCoord(name_x, name_y, "name_field")
GetCoord(addr_x, addr_y, "address_field")
GetCoord(dob_x,  dob_y,  "date_of_birth_field")
GetCoord(age_x,  age_y,  "age_field")
GetCoord(sex_x,  sex_y,  "sex_field")
GetCoord(add_x,  add_y,  "add_button")

if !WinExist(TargetTitle) {
    MsgBox, 16, Agent3 Error, VM window "%TargetTitle%" not found.
    ExitApp
}
WinActivate, %TargetTitle%
WinWaitActive, %TargetTitle%, , 4
WinGetPos, wx, wy, ww, wh, %TargetTitle%
CoordMode, Mouse, Screen
Sleep, 250

Status("Name")
FillField(wx+name_x, wy+name_y, name)

Status("Address")
FillField(wx+addr_x, wy+addr_y, address)

Status("DOB")
FillField(wx+dob_x,  wy+dob_y,  dob)

Status("Age")
FillField(wx+age_x,  wy+age_y,  age)

Status("Sex")
FillSex(wx+sex_x,    wy+sex_y,  sex)

Status("Click Add")
MouseMove, wx + add_x, wy + add_y, 0
Click
Sleep, 250
Status("Done")
Sleep, 500
Tooltip
ExitApp

FillField(X, Y, text) {
    MouseMove, X, Y, 0
    Click
    Sleep, 120
    Send, ^a
    Sleep, 80
    Send, {Backspace}
    Sleep, 100
    if (text != "") {
        ClipSaved := ClipboardAll
        Clipboard := ""
        Clipboard := text
        ClipWait, 1
        Send, ^v
        Sleep, 120
        Clipboard := ClipSaved
    }
}

FillSex(X, Y, val) {
    MouseMove, X, Y, 0
    Click
    Sleep, 120
    Send, ^a
    Sleep, 80
    Send, {Backspace}
    Sleep, 100
    v := Trim(val)
    if (v = "")
        return
    first := SubStr(v, 1, 1)
    first := RegExReplace(first, ".*", "$U0")  ; uppercase
    if (first = "M" || first = "F") {
        Send, %first%
    } else {
        Send, !{Down}
        Sleep, 150
        Send, %first%
        Sleep, 150
        Send, {Enter}
    }
}

Status(msg){
    Tooltip, Agent3: %msg%
    Sleep, 150
}
