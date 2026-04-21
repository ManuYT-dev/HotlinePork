import pygame
from modules.General.types import InputType
from modules.General.functions import SaveData
from modules.General.globals import changeable_values

controlls_data = SaveData(changeable_values.DEFAULT_PATH + r"/assets/saved_datas/controlls.json")

MOUSE_BUTTONS = {"LEFT": [InputType.MOUSE, pygame.BUTTON_LEFT],
                "MIDDLE": [InputType.MOUSE, pygame.BUTTON_MIDDLE],
                "RIGHT": [InputType.MOUSE, pygame.BUTTON_RIGHT]}

DEFAULT_KEYS = {"UP": [(InputType.KEYBOARD, pygame.K_w), (InputType.KEYBOARD, pygame.K_UP)],
            "LEFT": [(InputType.KEYBOARD, pygame.K_a), (InputType.KEYBOARD, pygame.K_LEFT)],
            "DOWN": [(InputType.KEYBOARD, pygame.K_s), (InputType.KEYBOARD, pygame.K_DOWN)],
            "RIGHT": [(InputType.KEYBOARD, pygame.K_d), (InputType.KEYBOARD, pygame.K_RIGHT)],
            "SHOOTING": [(InputType.KEYBOARD, pygame.K_SPACE), (InputType.MOUSE, pygame.BUTTON_LEFT)],
            "DROP ITEM": [(InputType.KEYBOARD, pygame.K_q), (InputType.MOUSE, pygame.BUTTON_RIGHT)],
            "PICKUP ITEM": [(InputType.KEYBOARD, pygame.K_e), (None, None)],
            "LOOK AROUND": [(InputType.KEYBOARD, pygame.K_c), (InputType.KEYBOARD, pygame.K_LCTRL)]}

ALL_KEYS = controlls_data.data if controlls_data.data != {} else DEFAULT_KEYS

MOVEMENT_KEYS = ALL_KEYS["UP"] + ALL_KEYS["LEFT"] + ALL_KEYS["DOWN"] + ALL_KEYS["RIGHT"]

SHOOT_KEYS = ALL_KEYS["SHOOTING"]

DROP_WEAPON_KEYS = ALL_KEYS["DROP ITEM"]

PICK_UP_WEAPON = ALL_KEYS["PICKUP ITEM"]

CAMERA_LOOK_AROUND = ALL_KEYS["LOOK AROUND"]

def update_all_keys(data: dict[str, list[tuple[str, int]]]): # ES ISCH SO HÄSSLICH UND WIDERLICH ABER ES MUSS SO😢😢😢😢😢😢😢
    global ALL_KEYS, MOVEMENT_KEYS, SHOOT_KEYS, DROP_WEAPON_KEYS, PICK_UP_WEAPON, CAMERA_LOOK_AROUND
    ALL_KEYS = data
    MOVEMENT_KEYS = ALL_KEYS["UP"] + ALL_KEYS["LEFT"] + ALL_KEYS["DOWN"] + ALL_KEYS["RIGHT"]
    SHOOT_KEYS = ALL_KEYS["SHOOTING"]
    DROP_WEAPON_KEYS = ALL_KEYS["DROP ITEM"]
    PICK_UP_WEAPON = ALL_KEYS["PICKUP ITEM"]
    CAMERA_LOOK_AROUND = ALL_KEYS["LOOK AROUND"]