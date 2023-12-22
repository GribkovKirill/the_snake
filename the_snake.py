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

# Цвета
colors = {
    'black': (0, 0, 0),
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'CONTOUR': (93, 216, 228)
}
BOARD_BACKGROUND_COLOR = colors['black']
snake_color = colors['green']
apple_color = colors['red']
bad_apple_color = colors['blue']
CONTOUR_COLOR = colors['CONTOUR']
# Скорость движения змейки
SPEED = 10

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Заголовок окна игрового поля
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()


# Описания классов игры.
class GameObject:
    """Базовый класс через который инициализируются свойства и
    методы классов игровых объектов.
    """

    def __init__(
            self,
            body_color=BOARD_BACKGROUND_COLOR,
            position=center
    ):
        self.body_color = body_color
        self.position = position
        self.draw

    def draw(self):
        """Это абстрактный метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект будет
        отрисовываться на экране. По умолчанию — pass.
        """
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, CONTOUR_COLOR, rect, 1)


class Apple(GameObject):
    """Класс описывающий поведение яблок."""

    def randomize_position(self):
        """Устанавливаем яблоко в случайное место."""
        return (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def __init__(self, body_color=apple_color):
        self.position = self.randomize_position()
        self.body_color = body_color


class Snake(GameObject):
    """Класс описывающий поведение змейки."""

    direction = RIGHT
    next_direction = None

    def __init__(self,
                 position=center):
        self.position = position  # Если возможно объясните мне необходимость
        self.body_color = snake_color  # в создании атрибута position.
        self.positions = [position]
        self.length = len(self.positions)

    def update_direction(self):
        """Метод изменения направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Метод отрисовки змейки."""
        for self.position in self.positions[:-1]:
            super().draw()

        # Отрисовка головы змейки
        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, CONTOUR_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, last_rect
            )

    def eat_bad_apple(self, screen):
        """Метод отрисовывающий ситуацию поедания плохого яблока."""
        if isinstance(self.eat_bad, tuple):
            bad_rect = pygame.Rect(
                (self.eat_bad[0], self.eat_bad[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, bad_rect
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
        self.last = self.positions[-1]
        self.eat_bad = self.positions[-2]  # Случай плохого яблока.

    def get_head_position(self):
        """Получаем координаты головы змейки
        для проверки на игровые события.
        """
        return self.positions[0]

    def reset(self):
        """Сброс состояния змейки при проигрыше."""
        self.__init__(position=center)
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        screen.fill(BOARD_BACKGROUND_COLOR)


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


def game_over(snake, apple, bad_apple):
    """Функция отрабатывает ситуацию проигрыша."""
    snake.reset()
    apple.position = apple.randomize_position()
    bad_apple.position = bad_apple.randomize_position()


def drop_empty(apple, snake, apple_in_ground):
    """Функция отрабатывает падение яблок
    строго на незанятые участки.
    """
    while True:
        apple.position = apple.randomize_position()
        union_list = snake.positions + [apple_in_ground.position]

        if (apple.position not in union_list):
            break


def main():
    """Тут находятся экземпляры классов."""
    snake = Snake(position=center)
    apple = Apple(body_color=apple_color)
    bad_apple = Apple(body_color=bad_apple_color)

    while True:
        """В теле цикла основные механики
        обработки действий в игре и игровых ситуаций.
        """
        clock.tick(SPEED)
        handle_keys(snake)  # Нажатие.
        snake.update_direction()  # изменение в методе.
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
            if len(snake.positions) > 2:
                snake.eat_bad_apple(screen)
                del snake.positions[-2:]
                drop_empty(bad_apple, snake, apple)

            # Если змейке некуда уменьшаться игра перезапускается.
            else:
                game_over(snake, apple, bad_apple)

        # Если змейка не съела в этот такт яблоко.
        elif snake.get_head_position() != apple.position:
            del snake.positions[-1]

        # Если змейка съела яблоко.
        else:
            drop_empty(apple, snake, bad_apple)
        pygame.display.update()


if __name__ == '__main__':
    main()
