from random import randint, choice
from time import sleep


# Проверка ошибок
class BoardOutException(Exception):
    pass

class BoardWrongShipException(BoardOutException):
    pass

class BoardUsedException(BoardOutException):
    def __str__(self):
        return 'В эту клетку уже стреляли!'

# Логика попаданий
class Dot:
    def __init__(self, x, y):
        self.x = x  # Координата X
        self.y = y  # Координата Y

    def __eq__(self, other):  # Сравнение координат
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

# Логика корабля
class Ship:
    def __init__(self, point: Dot, length: int, orientation: bool):
        self.point = point
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            coor_x = self.point.x
            coor_y = self.point.y
            if self.orientation:
                coor_y += i
            else:
                coor_x += i
            ship_dots.append(Dot(coor_x, coor_y))  # Отметка попадания
        return ship_dots

    def hit(self, dot) -> bool:
        return dot in self.dots

# Логика Доски
class Board:
    def __init__(self, size: int, hid=False):
        self.size = size
        self.hid = hid
        self.field = [['0'] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.lasthit = []  # Список ранений корабля
        self.count_burn_ships = 0  # Счетчик

    def __str__(self):
        b = '  | ' + ' | '.join(map(str, range(1, self.size + 1)))
        for i, row in enumerate(self.field):
            b += f'\n{i + 1} | ' + ' | '.join(row) #Разделители
        if self.hid:
            b = b.replace('■', '0') #Скрытие кораблей бота
        return b

    def out(self, d: Dot) -> bool:
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def outlining(self, ship, visible=False):
        arround = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        for dot in ship.dots:
            for dx, dy in arround:
                coor_dot = Dot(dot.x + dx, dot.y + dy)
                if not self.out(coor_dot) and coor_dot not in self.busy:
                    if visible:
                        self.field[coor_dot.x][coor_dot.y] = '●'  # Символ при промахе
                    self.busy.append(coor_dot)

    def add_ship(self, ship): #Установка кораблей
        for d in ship.dots:
            if d in self.busy or self.out(d):
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        self.ships.append(ship)
        self.outlining(ship)

    def shot(self, d: Dot) -> bool:
        if d in self.busy:
            raise BoardUsedException()
        if self.out(d):
            raise BoardOutException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.hit(d):
                self.field[d.x][d.y] = 'X' #Символ при попадании
                print('Попал!')
                ship.lives -= 1
                if ship.lives == 0:
                    self.count_burn_ships += 1
                    self.outlining(ship, visible=True)
                    print('Корабль уничтожен!')
                    self.lasthit = []
                    return False
                else:
                    print('Корабль горит!')
                    self.lasthit.append(d)
                    return True

        self.field[d.x][d.y] = '●'
        print('Промах!')
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count_burn_ships == len(self.ships)

class Player:
    def __init__(self, board: Board, enemy: Board):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self) -> bool:
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                sleep(1)
                return repeat
            except BoardOutException as exc:
                print(exc)

#Логика AI
class BOT(Player):
    def ask(self) -> Dot:
        last = self.enemy.lasthit
        while True:
            if last:
                if len(last) == 1:
                    near = ((0, 1), (0, -1), (1, 0), (-1, 0))
                else:
                    if last[0].x == last[-1].x:
                        near = ((0, 1), (0, -1))
                    else:
                        near = ((1, 0), (-1, 0))
                dx, dy = choice(near)
                d = choice((Dot(last[-1].x + dx, last[-1].y + dy), Dot(last[0].x + dx, last[0].y + dy)))
            else:
                d = Dot(randint(0, 5), randint(0, 5))
            if d not in self.enemy.busy and not self.enemy.out(d):
                break
        sleep(0.1 * randint(15, 60))
        print(f'Бот бьет: {d.x + 1} {d.y + 1}')
        sleep(0.1 * randint(15, 30))
        return d

class User(Player):
    def ask(self) -> Dot:
        while True:
            coords = input('Введите координаты выстрела через пробел:\t').split()
            if len(coords) != 2:
                print('Введите 2 координаты')
                continue
            x, y = coords
            if not all((x.isdigit(), y.isdigit())):
                print('Координаты должны быть цифрами')
                continue
            return Dot(int(x) - 1, int(y) - 1)

class Game:
    def __init__(self, size=6):
        self.lens = (3, 2, 2, 1, 1, 1, 1)
        self.size = size
        bot_board = self.random_board()
        user_board = self.random_board()
        bot_board.hid = True

        self.bot = BOT(bot_board, user_board)
        self.player = User(user_board, bot_board)

    def generation_board(self): #Генерация поля боя
        attempts = 0
        board = Board(size=self.size)
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), l, bool(randint(0, 1)))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.generation_board()
        return board

    def show_board(self):
        print('-' * self.size * 10)
        print('Ваша доска:'.ljust((self.size + 1) * 4 - 1) + ' ' * self.size + 'Доска Бота:')
        for s1, s2 in zip(self.player.board.__str__().split('\n'), self.bot.board.__str__().split('\n')):
            print(s1 + ' ' * self.size + s2)

    def loop(self):
        step = 0
        while True:
            self.show_board()
            if step % 2 == 0:
                print('Ваш ход!')
                repeat = self.player.move()
            else:
                print('Ход противника')
                repeat = self.bot.move()
            if repeat:
                step -= 1

            if self.bot.board.defeat():
                self.show_board()
                print('Вы победили!')
                break
            if self.player.board.defeat():
                self.show_board()
                print('Вы проиграли!')
                break
            step += 1

    def start(self):
        self.loop()

g = Game()
g.start()