import os
import sys
from multiprocessing import freeze_support
freeze_support()

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

if __name__ == "__main__":
    import pygame
    pygame.init()
    from modules.General.globals import changeable_values
    from modules.General.globals import SCREEN_SIZE

    if getattr(sys, 'frozen', False):
        asset_path = sys._MEIPASS        # Assets aus dem Bundle
        save_path = os.path.dirname(sys.executable)  # Saves neben der EXE
    else:
        asset_path = os.path.dirname(os.path.abspath(__file__))
        save_path = asset_path

    screen = pygame.display.set_mode((SCREEN_SIZE[0], SCREEN_SIZE[1]))
    pygame.display.set_icon(pygame.image.load(os.path.join(asset_path, "assets", "icon.ico")))
    pygame.display.set_caption("HOTLINE PORK")

    changeable_values.SCREEN = screen
    changeable_values.DEFAULT_PATH = asset_path
    changeable_values.SAVE_PATH = save_path

    from modules.Menu.menu import MainMenuApp
    MainMenuApp().run()