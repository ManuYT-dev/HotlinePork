import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
if __name__ == "__main__":
    import pygame
    pygame.init()
    from modules.General.globals import changeable_values
    from modules.General.globals import SCREEN_SIZE

    screen = pygame.display.set_mode((SCREEN_SIZE[0], SCREEN_SIZE[1]))
    path = os.path.dirname(os.path.abspath(__file__))
    pygame.display.set_icon(pygame.image.load(path + "/assets/icon.ico"))
    pygame.display.set_caption("HOTLINE PORK")

    changeable_values.SCREEN = screen
    changeable_values.DEFAULT_PATH = path

    from modules.Menu.menu import MainMenuApp

    MainMenuApp().run()
