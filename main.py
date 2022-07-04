import pymem
import time
import keyboard
from threading import Thread
import math

pm = pymem.Pymem("csgo.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

dwGlowObjectManager = int(0x5318E50)
dwEntityList = int(0x4DD0AB4)
dwLocalPlayer = int(0xDB558C)
dwForceJump = int(0x527A9AC)
dwClientState = int(0x589FC4)
m_iShotsFired = int(0x103E0)
dwClientState_ViewAngles = int(0x4D90)
m_aimPunchAngle = int(0x303C)

m_fFlags = int(0x104)

m_iTeamNum = int(0xF4)
m_iGlowIndex = int(0x10488)

def ESP():
    while True:
        player = pm.read_int(client + dwLocalPlayer)
        glow_manager = pm.read_int(client + dwGlowObjectManager)

        if (player):
            team = pm.read_int(player + m_iTeamNum)

            for i in range(1, 32):
                entity = pm.read_int(client + dwEntityList + i * 0x10)

                if (entity):
                    entity_team_id = pm.read_int(entity + m_iTeamNum)
                    entity_glow_object = pm.read_int(entity + m_iGlowIndex)

                    if entity_team_id != team:
                        pm.write_float(glow_manager + entity_glow_object * 0x38 + 0x8, float(1))
                        pm.write_float(glow_manager + entity_glow_object * 0x38 + 0xC, float(1))
                        pm.write_float(glow_manager + entity_glow_object * 0x38 + 0x10, float(0))
                        pm.write_float(glow_manager + entity_glow_object * 0x38 + 0x14, float(1))

                        pm.write_int(glow_manager + entity_glow_object * 0x38 + 0x28, 1)
        time.sleep(0.01)

def Bhop():
    while True:
        if pm.read_int(client + dwLocalPlayer):
            player = pm.read_int(client + dwLocalPlayer)
            force_jump = client + dwForceJump
            on_ground = pm.read_int(player + m_fFlags)

            if keyboard.is_pressed('space'):
                if on_ground == 257:
                    pm.write_int(force_jump, 5)
                    time.sleep(0.07)
                    pm.write_int(force_jump, 4)

def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX < -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < -180:
        viewAngleY += 360
    return viewAngleX, viewAngleY

def checkangles(x, y):
    if x > 89:
        return False
    elif x < -89:
        return False
    elif y > 360:
        return False
    elif y < -360:
        return False
    else:
        return True

def nanchecker(first, second):
    if math.isnan(first) or math.isnan(second):
        return False
    else:
        return True

def RCS():
    oldpunchx = 0.0
    oldpunchy = 0.0

    while True:
        try:
            rcslocalplayer = pm.read_int(client + dwLocalPlayer)
            rcsengine = pm.read_int(engine + dwClientState)

            if pm.read_int(rcslocalplayer + m_iShotsFired) > 2:
                rcs_x = pm.read_float(rcsengine + dwClientState_ViewAngles)
                rcs_y = pm.read_float(rcsengine + dwClientState_ViewAngles + 0x4)
                punchx = pm.read_float(rcslocalplayer + m_aimPunchAngle)
                punchy = pm.read_float(rcslocalplayer + m_aimPunchAngle + 0x4)
                newrcsx = rcs_x - (punchx - oldpunchx) * (50 * 0.02)
                newrcsy = rcs_y - (punchy - oldpunchy) * (50 * 0.02)
                newrcs, newrcy = normalizeAngles(newrcsx, newrcsy)
                oldpunchx = punchx
                oldpunchy = punchy
                if nanchecker(newrcsx, newrcsy) and checkangles(newrcsx, newrcsy):
                    pm.write_float(rcsengine + dwClientState_ViewAngles, newrcsx)
                    pm.write_float(rcsengine + dwClientState_ViewAngles + 0x4, newrcsy)
            else:
                oldpunchx = 0.0
                oldpunchy = 0.0
                newrcsx = 0.0
                newrcsy = 0.0
        except:
            pass

Thread(target=Bhop).start()
Thread(target=ESP).start()