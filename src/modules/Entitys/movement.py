import pygame
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement

def LOS(starting_point: pygame.Vector2,
        end_point: pygame.Vector2,
        blocking: pygame.FRect | list[pygame.FRect],
        max_distance: int = 1000,
        steps: int = 5, 
        visuals_toggled: bool = False,
        screen: pygame.Surface = None,
        show_error_messages: bool = True) -> bool:
    """
    Performs a line-of-sight check between two points.

    Args:
        starting_point (pygame.Vector2): The starting point of the line-of-sight check.
        end_point (pygame.Vector2): The end point of the line-of-sight check.
        blocking (pygame.FRect | list[pygame.FRect]): The blocking objects to check against.
        max_distance (int, optional): The maximum distance to check. Defaults to 1000.
        steps (int, optional): The number of steps to take when checking. Defaults to 5.
        visuals_toggled (bool, optional): Whether to draw debugging circles. Defaults to False.
        screen (pygame.Surface, optional): The screen to draw debugging circles on. Defaults to None.

    Returns:
        bool: A boolean indicating whether the line-of-sight check passes.

    Raises:
        ValueError: If `max_distance` or `steps` are not positive integers.
        TypeError: If `blocking` is not a pygame.FRect or a list of pygame.FRect.
        TypeError: If `end_point` or `starting_point` are not pygame.Vector2.
        TypeError: If `visuals_toggled` is not a boolean.
        TypeError: If `screen` is not a pygame.Surface when `visuals_toggled` is True.
    """
    if show_error_messages:
        if not isinstance(max_distance, int) or max_distance < 1:
            raise ValueError("max_distance must be a positive integer")
        if not isinstance(steps, int) or steps < 1:
            raise ValueError("steps must be a positive integer")
        if not isinstance(blocking, (pygame.FRect, list)):
            raise TypeError("blocking must be a pygame.FRect or a list of pygame.FRect")
        if not isinstance(end_point, pygame.Vector2):
            raise TypeError("end_point must be a pygame.Vector2")
        if not isinstance(starting_point, pygame.Vector2):
            raise TypeError("starting_pos must be a pygame.Vector2")
        if not isinstance(visuals_toggled, bool):
            raise TypeError("visuals_toggled must be a boolean")
        if visuals_toggled is True:
            if not isinstance(screen, pygame.Surface):
                raise TypeError("screen must be a pygame.Surface")

    blocking_list: list[pygame.FRect] | pygame.sprite.Group = blocking if isinstance(blocking, (list, pygame.sprite.Group)) else [blocking]
    max_distance_square: int = max_distance ** 2

    return process_date(starting_point, end_point, blocking_list, steps, max_distance_square, visuals_toggled, screen)

def check_blocking(_pos: pygame.Vector2,
                    _blocking_list: list[pygame.FRect]) -> bool:
    """
    Determines if a given position is blocked by any of the provided blocking rectangles.

    Args:
        _pos (pygame.Vector2): The position to check for blocking.
        _blocking_list (list[pygame.FRect]): A list of blocking rectangles to check against.

    Returns:
        bool: True if the position is within any of the blocking rectangles, False otherwise.
    """

    x, y = int(_pos.x), int(_pos.y)
    for block in _blocking_list:
        if block.collidepoint(x, y):
            return True
    return False

def process_date(starting_pos: pygame.Vector2,
                 end_pos: pygame.Vector2,
                 blocking_list: list[pygame.FRect],
                 steps: int = 5,
                 max_distance_sq: int = 1000 ** 2,
                 visuals_toggled: bool = False,
                 screen: pygame.Surface = None) -> bool:
    """
    Performs a line-of-sight check between two points with the given number of steps.

    Args:
        starting_pos (pygame.Vector2): The starting position to check from.
        end_pos (pygame.Vector2): The ending position to check to.
        blocking_list (list[pygame.FRect]): A list of blocking rectangles to check against.
        steps (int, optional): The number of steps to take when checking. Defaults to 5.
        max_distance_sq (int, optional): The maximum distance to check squared. Defaults to 1000000.
        visuals_toggled (bool, optional): Whether to draw debugging circles. Defaults to False.
        screen (pygame.Surface, optional): The screen to draw debugging circles on. Defaults to None.

    Returns:
        bool: True if the line-of-sight check is successful, False otherwise.
    """
    if abs((end_pos - starting_pos).length_squared()) > max_distance_sq:
        return False

    if starting_pos == end_pos:
        return True

    direction = (end_pos - starting_pos).normalize()
    steps_needed = int(starting_pos.distance_to(end_pos) / steps) + 1

    for i in range(steps_needed):
        current_pos = starting_pos + direction * (steps * i)
        
        if visuals_toggled and i % 5 == 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(current_pos.x), int(current_pos.y)), 2)
        
        if check_blocking(current_pos, blocking_list):
            return False
    return True

def a_star(
    starting_position: pygame.Vector2,
    target_position: pygame.Vector2,
    blocking: list[pygame.FRect],
    screen_width: int = 1000,
    screen_height: int = 1000,
    buffer: tuple[int, int] | list[int] | pygame.Vector2= (30, 20),
    surface: pygame.Surface = None,
    show_visuals: bool = False,
    show_error_messages: bool = True
) -> list[pygame.Vector2]:
    """
    Performs an A* pathfinding algorithm to find the shortest path from the
    enemy's current position to the given target position.

    Args:
        target_position (pygame.Vector2): The target position to find the path to.
        blocking (list[pygame.FRect]): A list of blocking rectangles to avoid.
        screen_width (int, optional): The width of the screen. Defaults to 1000.
        screen_height (int, optional): The height of the screen. Defaults to 1000.
        buffer (tuple[int, int], optional): A buffer to apply to the blocking rectangles.
            Defaults to (30, 20).

    Returns:
        list[pygame.Vector2]: A list of positions representing the shortest path from
            the enemy's current position to the target position. If no path is found,
            an empty list is returned.
    """
    if show_error_messages:
        if not isinstance(target_position, pygame.Vector2): raise TypeError("target_position must be a pygame.Vector2")
        if not isinstance(blocking, list): raise TypeError("blocking must be a list")
        if not isinstance(screen_width, int): raise TypeError("screen_width must be an int")
        if not isinstance(screen_height, int): raise TypeError("screen_height must be an int")
        if not isinstance(buffer, tuple | list | pygame.Vector2): raise TypeError("buffer must be a tuple")
        if not isinstance(show_visuals, bool): raise TypeError("show_visuals must be a boolean")
        if not isinstance(surface, pygame.Surface) and show_visuals: raise TypeError("surface must be a pygame.Surface when show_visuals is True")
    try:
        grid_size = 10
        width = screen_width // grid_size
        height = screen_height // grid_size

        matrix = [[1] * width for _ in range(height)]

        for block in blocking:
            block_x1 = max(0, int((block.left - buffer[0]) / grid_size))
            block_y1 = max(0, int((block.top - buffer[1]) / grid_size))
            block_x2 = min(width - 1, int((block.right + buffer[0]) / grid_size))
            block_y2 = min(height - 1, int((block.bottom + buffer[1]) / grid_size))

            for y in range(block_y1, block_y2 + 1):
                for x in range(block_x1, block_x2 + 1):
                    matrix[y][x] = 0

        grid = Grid(matrix=matrix)

        start_x = max(0, min(int(starting_position.x / grid_size), width - 1))
        start_y = max(0, min(int(starting_position.y / grid_size), height - 1))
        start = grid.node(start_x, start_y)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)

        end_x: int = max(0, min(int(target_position.x / grid_size), width - 1))
        end_y: int = max(0, min(int(target_position.y / grid_size), height - 1))
        end = grid.node(end_x, end_y)

        path, _ = finder.find_path(start, end, grid)
        if path:
            returning = [pygame.Vector2(x * grid_size + grid_size / 2, y * grid_size + grid_size / 2) for x, y in path]
            if show_visuals:
                pygame.draw.lines(surface, (255, 0, 0), False, returning, 5)

            return returning

        return []

    except Exception as e:
        print(f"[A* ERROR] {e}")
        return []