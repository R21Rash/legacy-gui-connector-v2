#NoEnv
#SingleInstance Force
SetTitleMatchMode, 2
DetectHiddenWindows, On
SendMode, Input

if (A_Args.Length() < 1) {
    MsgBox, 16, Probe Error, Missing INI path. Usage: AutoHotkey.exe agent3_probe.ahk "path\agent3_payload.ini"
    ExitApp
}
ini := A_Args[1]

IniRead, TargetTitle, %ini%, General, window_title, WinXP for VB6

GetCoord(ByRef outx, ByRef outy, key) {
    global ini
    IniRead, raw, %ini%, Coords, %key%
    StringSplit, parts, raw, `,
    outx := parts1, outy := parts2
}

GetCoord(name_x, name_y, "name_field")
GetCoord(addr_x, addr_y, "address_field")
GetCoord(dob_x,  dob_y,  "date_of_birth_field")
GetCoord(age_x,  age_y,  "age_field")
GetCoord(sex_x,  sex_y,  "sex_field")
GetCoord(add_x,  add_y,  "add_button")

if !WinExist(TargetTitle) {
    MsgBox, 16, Probe Error, VM window "%TargetTitle%" not found.
    ExitApp
}
WinActivate, %TargetTitle%
WinWaitActive, %TargetTitle%, , 3
WinGetPos, wx, wy, ww, wh, %TargetTitle%
CoordMode, Mouse, Screen

Show("NAME",   wx+name_x, wy+name_y)
Show("ADDR",   wx+addr_x, wy+addr_y)
Show("DOB",    wx+dob_x,  wy+dob_y)
Show("AGE",    wx+age_x,  wy+age_y)
Show("SEX",    wx+sex_x,  wy+sex_y)
Show("ADD BTN",wx+add_x,  wy+add_y)
MsgBox, 64, Probe, Done. If markers weren’t on the controls, re-run calibration and ensure 100% scale.

Show(label, X, Y) {
    Tooltip, %label%, X+14, Y-22
    MouseMove, X, Y, 0
    DllCall("user32.dll\InvertRect", "Ptr", DllCall("GetDC", "Ptr", 0, "Ptr"), "Ptr", CreateRect(X-10,Y-10,X+10,Y+10))
    Sleep, 600
    Tooltip
}
CreateRect(x1,y1,x2,y2){
    VarSetCapacity(RECT, 16, 0)
    NumPut(x1, RECT, 0, "Int"), NumPut(y1, RECT, 4, "Int"), NumPut(x2, RECT, 8, "Int"), NumPut(y2, RECT, 12, "Int")
    return &RECT
}
