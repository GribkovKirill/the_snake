from random import choice, randint
from string import Template

import pygame

# Инициализация PyGame
pygame.init()

# Константы для размеров
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Изменения направлений
NEXT_DIRECTION = {
    (LEFT, pygame.K_UP): UP,
    (RIGHT, pygame.K_UP): UP,
    (UP, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_LEFT): LEFT,
    (LEFT, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_DOWN): DOWN,
    (UP, pygame.K_RIGHT): RIGHT,
    (DOWN, pygame.K_RIGHT): RIGHT,
}


class Color:
    """Константы цветов."""

    BLACK = (0, 0, 0),
    GREEN = (0, 255, 0),
    RED = (255, 0, 0),
    BLUE = (0, 0, 255),
    CONTOUR = (93, 216, 228)


BOARD_BACKGROUND_COLOR = Color.BLACK
SNAKE_COLOR = Color.GREEN
APPLE_COLOR = Color.RED
BAD_APPLE_COLOR = Color.BLUE
CONTOUR_COLOR = Color.CONTOUR


# Скорость движения змейки и рекорд за сессию
class GameSettings:
    """Класс с игровыми настройками."""

    SPEED = 10
    RECORD = 0
    CAP_STRING = Template(  # Так чтоли?
            'Змейка. Чтобы выйти нажмите "Закрыть". '
            'Скорость: $speed. Рекорд: $record. '
            'Изменить скорость: pg_up pg_down'
    )

    @classmethod
    def cap(cls):
        """Метод с информацией об игре в шапке окна."""
        return (
            cls.CAP_STRING.substitute(speed=cls.SPEED, record=cls.RECORD)
        )

    @classmethod
    def speed_change(cls, changer):
        """Метод для изменения скорости движения змейки."""
        if changer == pygame.K_PAGEDOWN:
            cls.SPEED -= 1
        elif changer == pygame.K_PAGEUP:
            cls.SPEED += 1

    @classmethod
    def new_record(cls, new_record):
        """Метод обновляющий рекорд за сессию."""
        cls.RECORD = new_record


# Инициализацияигрового поля.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля.
pygame.display.set_caption(GameSettings.cap())

# Настройка времени.
clock = pygame.time.Clock()


# Описания классов игры.
class GameObject:
    """Базовый класс через который инициализируются свойства и
    методы классов игровых объектов.
    """

    def __init__(
            self,
            body_color=BOARD_BACKGROUND_COLOR,
            position=CENTER
    ):
        self.body_color = body_color
        self.position = position

    def draw(self, color, position, contour_color=CONTOUR_COLOR):
        """Это абстрактный метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект будет
        отрисовываться на экране. По умолчанию — pass.
        """
        rect = pygame.Rect(
            (position[0], position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, contour_color, rect, 1)


class Apple(GameObject):
    """Класс описывающий поведение яблок."""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.position = self.randomize_position()

    def randomize_position(self):
        """Устанавливаем яблоко в случайное место."""
        return (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self):
        """Метод отрисовывающий яблоко."""
        return super().draw(self.body_color, self.position)


class Snake(GameObject):
    """Класс описывающий поведение змейки."""

    def __init__(self, body_color=SNAKE_COLOR, position=CENTER):
        super().__init__(body_color)
        self.positions = [position]
        self.length = 1
        self.direction = RIGHT

    def update_direction(self, next_direction):
        """Метод изменения направления движения."""
        self.direction = next_direction

    def draw(self):
        """Метод отрисовки змейки."""
        # Отрисовка головы змейки
        super().draw(self.body_color, self.positions[0])

        # Затирание последнего сегмента
        super().draw(
            BOARD_BACKGROUND_COLOR, self.positions[-1], BOARD_BACKGROUND_COLOR
        )

    def eat_bad_apple(self):
        """Метод отрисовывающий ситуацию поедания плохого яблока."""
        super().draw(
            BOARD_BACKGROUND_COLOR, self.positions[-2], BOARD_BACKGROUND_COLOR
        )

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

    def get_head_position(self):
        """Получаем координаты головы змейки
        для проверки на игровые события.
        """
        return self.positions[0]

    def reset(self, position=CENTER):
        """Сброс состояния змейки при проигрыше."""
        self.positions = [position]
        self.length = 1
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """# Функция обработки ввода движений."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            GameSettings.speed_change(event.key)
            next_direction = NEXT_DIRECTION.get(
                (game_object.direction, event.key)
            )
            if next_direction:
                return game_object.update_direction(next_direction)


def game_over(snake, apple, bad_apple):
    """Функция отрабатывает ситуацию проигрыша."""
    if GameSettings.RECORD < snake.length:
        GameSettings.new_record(snake.length)
    snake.reset()
    apple.position = apple.randomize_position()
    bad_apple.position = bad_apple.randomize_position()


def drop_empty(apple, snake, apple_in_ground):
    """Функция отрабатывает падение яблок
    строго на незанятые участки.
    """
    union_list = snake.positions + [apple_in_ground.position]

    while True:
        apple.position = apple.randomize_position()

        if apple.position not in union_list:
            break


def main():
    """Тут находятся экземпляры классов."""
    snake = Snake()
    apple = Apple()
    bad_apple = Apple(body_color=BAD_APPLE_COLOR)

    while True:
        """В теле цикла основные механики
        обработки действий в игре и игровых ситуаций.
        """
        clock.tick(GameSettings.SPEED)
        handle_keys(snake)  # Нажатие.
        snake.move()  # Движение змейки.
        apple.draw()  # Отрисовка яблока.
        bad_apple.draw()  # Плохого яблока.
        snake.draw()  # Змейки.

        # Если змейка врезалась в саму себя.
        if snake.get_head_position() in snake.positions[1:]:
            game_over(snake, apple, bad_apple)

        # Если змейка съела плохое яблоко.
        elif snake.get_head_position() == bad_apple.position:

            # Если длина змейки больше одного.
            if snake.length >= 2:
                snake.eat_bad_apple()
                del snake.positions[-2:]
                snake.length = len(snake.positions)
                drop_empty(bad_apple, snake, apple)

            # Если змейке некуда уменьшаться игра перезапускается.
            else:
                game_over(snake, apple, bad_apple)

        # Если змейка не съела в этот такт яблоко.
        elif snake.get_head_position() != apple.position:
            del snake.positions[-1]

        # Если змейка съела яблоко.
        else:
            snake.length = len(snake.positions)
            drop_empty(apple, snake, bad_apple)
        pygame.display.update()
        pygame.display.set_caption(GameSettings.cap())


if __name__ == '__main__':
    main()
