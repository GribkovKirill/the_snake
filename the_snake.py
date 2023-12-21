from random import choice, randint

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
    методы классов игровых объектов.
    """

    position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def __init__(self, body_color):
        self.body_color = body_color

    def draw(self):
        """Метод необходим для наследственных классов."""
        pass


class Apple(GameObjects):
    """Класс описывающий поведение яблока."""

    def randomize_position(self, total_x, total_y):
        """Устанавливаем яблоко в случайное место."""
        return (
            randint(0, GRID_WIDTH - 1) * 20,
            randint(0, GRID_HEIGHT - 1) * 20
        )

    def __init__(self):
        self.position = self.randomize_position(GRID_WIDTH, GRID_HEIGHT)
        self.body_color = (255, 0, 0)

    def draw(self, surface):
        """Отрисовка яблока."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (93, 216, 228), rect, 1)


class BadApple(Apple):
    """Класс описывающий поведение плохого яблока."""

    def __init__(self):
        self.position = self.randomize_position(GRID_WIDTH, GRID_HEIGHT)
        self.body_color = (0, 0, 255)

    def draw(self, surface):
        """Отрисовка плохого яблока."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (93, 216, 228), rect, 1)


class Snake(GameObjects):
    """Класс описывающий поведение змейки."""

    body_color = (0, 255, 0)
    direction = RIGHT
    next_direction = None

    def __init__(self):
        self.positions = [self.position]
        self.length = len(self.positions)

    def update_direction(self):
        """Метод изменения направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self, surface):
        """Метод отрисовки змейки."""
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

    def eat_bad_apple(self, surface):
        """Метод отрисовывающий ситуацию поедания плохого яблока."""
        if isinstance(self.eat_bad, tuple):
            bad_rect = pygame.Rect(
                (self.eat_bad[0], self.eat_bad[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, bad_rect)

    def move(self):
        """Метод движение змейки за счёт изменений списка."""
        step = map(lambda x: x * GRID_SIZE, self.direction)
        head = tuple(map(sum, zip(self.positions[0], step)))
        if head[0] == SCREEN_WIDTH:  # Переход правой границы.
            head = (0, head[1])
        elif head[0] < 0:  # Переход левой границы.
            head = (SCREEN_WIDTH - GRID_SIZE, head[1])
        elif head[1] == SCREEN_HEIGHT:  # Переход нижней границы.
            head = (head[0], 0)
        elif head[1] < 0:  # Переход верхней границы.
            head = (head[0], SCREEN_HEIGHT - GRID_SIZE)
        self.positions.insert(0, head)
        self.last = self.positions[-1]
        self.eat_bad = self.positions[-2]  # Случай плохого яблока.

    def get_head_position(self):
        """Получаем координаты головы змейки
        для проверки на игровые события.
        """
        return self.positions[0]

    def reset(self):
        """Сброс состояния змейки при проигрыше."""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.__init__()
        self.direction = choice((UP, DOWN, LEFT, RIGHT))


def handle_keys(game_object):
    """# Функция обработки ввода движений."""
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
    """Тут находятся экземпляры классов."""
    snake = Snake()
    apple = Apple()
    bad_apple = BadApple()

    while True:
        """В теле цикла основные механики
        обработки действий в игре и игровых ситуаций.
        """
        clock.tick(SPEED)
        handle_keys(snake)  # Нажатие.
        snake.update_direction()  # изменение в методе.
        snake.move()  # Движение змейки.
        apple.draw(screen)
        bad_apple.draw(screen)
        snake.draw(screen)

        # Если змейка врезалась в саму себя.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Если змейка съела плохое яблоко.
        elif snake.get_head_position() == bad_apple.position:

            # Если длина змейки больше одного.
            if len(snake.positions) > 2:
                snake.eat_bad_apple(screen)
                del snake.positions[-2:]

                # Цикл ограничения падения плохого яблока
                # на змейку и на яблоко.
                while True:
                    bad_apple.position = bad_apple.randomize_position(
                        SCREEN_WIDTH, SCREEN_HEIGHT
                    )
                    union_list = snake.positions + [apple.position]

                    if (bad_apple.position not in union_list):
                        break

            # Если змейке некуда уменьшаться игра перезапускается.
            else:
                snake.reset()

        # Если змейка не съела в этот такт яблоко.
        elif snake.get_head_position() != apple.position:
            del snake.positions[-1]

        # Если змейка съела яблоко.
        else:

            # Цикл ограничения падения яблока на змейку и на плохое яблоко.
            while True:
                apple.position = apple.randomize_position(
                    SCREEN_WIDTH, SCREEN_HEIGHT
                )
                union_list = snake.positions + [bad_apple.position]

                if (apple.position not in union_list):
                    break
        pygame.display.update()


if __name__ == '__main__':
    main()
