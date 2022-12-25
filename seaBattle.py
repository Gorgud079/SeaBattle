from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class BoardException(Exception):
    pass
class OutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы доски"
class UsedException(BoardException):
    def __str__(self):
        return "Уже стреляли в эту клетку"
class WrongShipException(BoardException):
    pass

# class Cell(object):
#     empty_cell = ' '
#     ship_cell = '■'
#     destroyed_ship = 'X'
#     damaged_ship = '□'
#     miss_cell = '•'

class Ship:
    def __init__(self, fore, length, orient):
        self.fore = fore
        self.length = length
        self.orient = orient
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            curr_x = self.fore.x
            curr_y = self.fore.y
            if self.orient == 0:
                curr_x += i
            elif self.orient == 1:
                curr_y += i
            ship_dots.append(Dot(curr_x, curr_y))
        return ship_dots
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        self.count = 0
        self.field = [["~"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self,ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise WrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                curr = Dot(d.x + dx, d.y + dy)
                if not (self.out(curr)) and curr not in self.busy:
                    if verb:
                        self.field[curr.x][curr.y] = "."
                        self.busy.append(curr)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace('■', "0")
        return res
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise OutException()
        if d in self.busy:
            raise UsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ход игрока.\n Введите координаты - ").split()
            if len(cords) != 2:
                print("Введите координаты корректно (x,y)")
                continue
            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print("Введите числа")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)
class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        board.begin()
        return board





    def greet(self):
        print("-" * 40)
        print("""\t\t ИГРА: Морской бой
        Введите координаты по Х и У оси:
             Х - номер строки
             У - номер столбца""")
        print("-" * 40)

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя: ")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера: ")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("*" * 20)
                print("""\\\\  // _ ||  ||  \\\\    //\\\\    // () ||  ||\n  ||  | |||  ||   \\\\  //  \\\\  //  || |\\\\ ||\n  ||  |_|\\\\_//     \\\\//    \\\\//   || | \\\\||""")
                print("*" * 20)
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("YOU LOSE")
                print("-" * 20)
                break
            num += 1
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()







# def start_table():
#     print(index := "_", "A", "B", "C", "D", "E", "F", "G", "H", sep=" | ")
#
#     for i, row in enumerate(field):
#         row_str = f"{i + 1}{' '.join(row)}"
#         print(row_str)
#
#     coord1 = input("?").upper()
#     column1 = index.find(coord1[0])
#     print(column1)
#     row1 = int(coord1[1])
#     print(row1, column1)
# field = [[" "] * 3 for i in range(6)]
# start_table()
