from random import choice, randint

from copy import deepcopy

import pygame

# Инициализация PyGame
pygame.init()

# Константы для размеров
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета фона - черный
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Скорость движения змейки
SPEED = 10

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()


# Описания классов игры.
class GameObjects:
    """Базовый класс через который инициализируются свойства и
    методы классов игровых объектов."""

    position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def __init__(self, body_color):
        """help."""
        self.body_color = body_color

    def draw(self):
        pass


class Apple(GameObjects):
    """Класс описывающий поведение яблока."""

    def randomize_position(self, total_x, total_y):
        return (
            randint(0, (total_x / 20) - 1) * 20,
            randint(0, (total_y / 20) - 1) * 20
        )

    def __init__(self):
        self.position = self.randomize_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.body_color = (255, 0, 0)

    def draw(self, surface):
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (93, 216, 228), rect, 1)


class Snake(GameObjects):
    """Класс описывающий поведение змейки."""
    body_color = (0, 255, 0)

    def __init__(self):

        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT
        self.next_direction = None
        self.head = self.positions[0]
        self.start_dict = deepcopy(self.__dict__)

    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self, surface):

        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (93, 216, 228), rect, 1)

        # Отрисовка головы змейки
        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, (93, 216, 228), head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        step = map(lambda x: x * 20, self.direction)
        head = tuple(map(sum, zip(self.positions[0], step)))
        if head[0] == 640:
            head = (0, head[1])
        elif head[0] < 0:
            head = (620, head[1])
        elif head[1] == 480:
            head = (head[0], 0)
        elif head[1] < 0:
            head = (head[0], 460)
        self.positions.insert(0, head)
        self.last = self.positions[-1]

    def get_head_position(self):
        return self.positions[0]

    def reset(self):
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.__init__()
        self.direction = choice((UP, DOWN, LEFT, RIGHT))


def handle_keys(game_object):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    # Тут нужно создать экземпляры классов
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)  # Нажатие.
        snake.update_direction()  # изменение в методе.
        snake.move()  # Движение змейки.
        apple.draw(screen)
        snake.draw(screen)
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
        elif snake.get_head_position() != apple.position:
            del snake.positions[-1]
        else:
            while True:
                """Цикл устраняющий возможность падения яблока на змею."""
                apple.position = apple.randomize_position(
                    SCREEN_WIDTH, SCREEN_HEIGHT
                )
                if apple.position not in snake.positions:
                    break
        pygame.display.update()


if __name__ == '__main__':
    main()
