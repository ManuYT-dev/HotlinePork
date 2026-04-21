import pygame
import os
import csv
from modules.General.functions import Camera

class globals:
    TILE_SIZE = 32

class TileMap:
    """
    A class representing a tile map.
    
    Attributes:
        tile_size (int): The size of a tile in pixels.
        final_tile_size (int): The final size of a tile in pixels.
        start_x (int): The x-coordinate of the top-left corner of the map.
        start_y (int): The y-coordinate of the top-left corner of the map.
        filename (str): The name of the file containing the map data.
        spritesheet (str): The path to the spritesheet image.
        map (list[list[str]]): A 2D list representing the map data.
        spritesheet (pygame.Surface): The spritesheet image.
        spritesheet_images_width (int): The number of images in the spritesheet in the x-direction.
        spritesheet_images_height (int): The number of images in the spritesheet in the y-direction.
        _spritetiles (dict[str, pygame.Surface]): A dictionary mapping sprite indices to their corresponding scaled surface.
        screen (pygame.Surface): The surface on which the map is drawn.
        camera (Camera): The camera object used for scrolling the map.
    
    Methods:
        _read_csv(): Reads the map data from a CSV file.
        _get_walls(): Calculates the walls of the map.
        _draw_init(): Initializes the map by drawing the visible tiles.
        draw_visible_tiles(): Draws the visible tiles on the screen."""
    def __init__(self,
                 filename: str,
                 spritesheet: str,
                 tile_size: int = 64,
                 final_tile_size: int = globals.TILE_SIZE):
        self.tile_size = tile_size
        self.final_tile_size = final_tile_size
        
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.filename = filename
        self.map = []
        self.spritesheet = pygame.image.load(spritesheet).convert_alpha()
        self.spritesheet_images_width: int = self.spritesheet.width // self.tile_size # Wieviel Bilder in der Breite
        self.spritesheet_images_height: int = self.spritesheet.height // self.tile_size # Wieviel Bilder in der Höhe
        self._spritetiles: dict[int: pygame.Surface] = {}
        self.walls: list[pygame.Rect] = []
        
        for i in range(self.spritesheet_images_width):
            for j in range(self.spritesheet_images_height):
                rect = pygame.Rect(i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size)
                img = pygame.transform.smoothscale(self.spritesheet.subsurface(rect), (self.final_tile_size, self.final_tile_size))
                self._spritetiles[str(i + j)] = img

        self._read_csv()
        self._get_walls()
        self._draw_init()
    
    def _read_csv(self):
        with open(os.path.join(self.filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                self.map.append(list(row))
        return self.map
    
    def _get_walls(self):
        for r_idx, row in enumerate(self.map):
            for c_idx, column in enumerate(row):
                if column != '0':
                    x = self.start_x + (c_idx * self.final_tile_size)
                    y = self.start_y + (r_idx * self.final_tile_size)
                    rect = pygame.Rect(x, y, self.final_tile_size, self.final_tile_size)
                    self.walls.append(rect)

    def _draw_init(self):
        self.screen = pygame.Surface((len(self.map[0]) * self.final_tile_size, len(self.map) * self.final_tile_size))
        for r_idx, row in enumerate(self.map):
            for c_idx, column in enumerate(row):
                spritesheet_index = column
                self.screen.blit(self._spritetiles[str(spritesheet_index)], (c_idx * self.final_tile_size, r_idx * self.final_tile_size))

    def draw(self,
             screen: pygame.Surface = None,
             camera: Camera = None) -> pygame.Surface | None:
        if screen:
            screen.blit(self.screen, (0, 0), camera.rect if camera else None)
            return

    def debug_draw_sprites(self, screen: pygame.Surface):
        for i in range(self.spritesheet_images_width):
            for j in range(self.spritesheet_images_height):
                screen.blit(self._spritetiles[i + j], (i * globals.TILE_SIZE, j * globals.TILE_SIZE))
    
    def draw_visible_tiles(self,
                           surface: pygame.Surface,
                           camera_rect: pygame.Rect):
        start_col = int(camera_rect.left // self.final_tile_size)
        end_col = int(camera_rect.right // self.final_tile_size) + 1
        start_row = int(camera_rect.top // self.final_tile_size)
        end_row = int(camera_rect.bottom // self.final_tile_size) + 1

        for row in range(start_row, end_row):
            if 0 <= row < len(self.map):
                for col in range(start_col, end_col):
                    if 0 <= col < len(self.map[row]):
                        tile_index = self.map[row][col]
                        tile = self._spritetiles[str(tile_index)]
                        x = col * self.final_tile_size
                        y = row * self.final_tile_size
                        surface.blit(tile, (x - camera_rect.left, y - camera_rect.top))
