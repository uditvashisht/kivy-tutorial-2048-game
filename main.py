from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import BorderImage, Color
from kivy.core.window import Window, Keyboard
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, NumericProperty
import random
from kivy.animation import Animation
from kivy.vector import Vector


spacing = 15

key_vectors = {Keyboard.keycodes['up']: (0, 1), Keyboard.keycodes['right']: (1, 0), Keyboard.keycodes['down']: (0, -1), Keyboard.keycodes['left']: (-1, 0)}

colors = ['EEE4DA', 'EDE0C8', 'F2B179', 'F59563', 'F67C5F', 'F65E3B', 'EDCF72', 'EDCC61', 'EDC850', 'EDC53F', 'EDC22E']

tile_colors = {2**i: color for i, color in enumerate(colors, start=1)}


def all_cells(flip_x=False, flip_y=False):
    for x in (reversed(range(4)) if flip_x else range(4)):
        for y in (reversed(range(4)) if flip_y else range(4)):
            yield (x, y)


class Tile(Widget):
    font_size = NumericProperty(24)
    number = NumericProperty(2)
    color = ListProperty(get_color_from_hex(tile_colors[2]))
    number_color = ListProperty(get_color_from_hex('776E65'))

    def __init__(self, number=2, **kwargs):
        super(Tile, self).__init__(**kwargs)
        self.font_size = 0.5 * self.width
        self.number = number
        self.update_colors()

    def update_colors(self):
        self.color = get_color_from_hex(tile_colors[self.number])
        if self.number > 4:
            self.number_color = get_color_from_hex('F9F6F2')

    def resize(self, pos, size):
        self.pos = pos
        self.size = size
        self.font_size = 0.5 * self.width


class Board(Widget):
    b = None
    moving = False

    def valid_cell(self, board_x, board_y):
        return (board_x >= 0 and board_y >= 0 and board_x <= 3 and board_y <= 3)

    def can_move(self, board_x, board_y):
        return (self.valid_cell(board_x, board_y) and self.b[board_x][board_y] is None)

    def is_deadlocked(self):
        for x, y in all_cells():
            if self.b[x][y] is None:
                return False
            number = self.b[x][y].number
            if self.can_merge(x + 1, y, number) or self.can_merge(x, y + 1, number):
                return False
        return True

    def new_tile(self, *args):
        empty_cells = [(x, y) for x, y in all_cells() if self.b[x][y] is None]
        x, y = random.choice(empty_cells)
        tile = Tile(pos=self.cell_pos(x, y), size=self.cell_size)
        self.b[x][y] = tile
        self.add_widget(tile)
        if len(empty_cells) == 1 and self.is_deadlocked():
            print('Game Over(board is deadlocked)')
        self.moving = False

    def reset(self):
        self.b = [[None for i in range(4)] for j in range(4)]
        self.new_tile()
        self.new_tile()

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.resize()

    def cell_pos(self, board_x, board_y):
        return (self.x + spacing + board_x * (self.cell_size[0] + spacing), self.y + spacing + board_y * (self.cell_size[1] + spacing))

    def can_merge(self, board_x, board_y, number):
        return (self.valid_cell(board_x, board_y) and self.b[board_x][board_y] is not None and self.b[board_x][board_y].number == number)

    def move(self, dir_x, dir_y):
        if self.moving:
            return

        for board_x, board_y in all_cells(dir_x > 0, dir_y > 0):
            tile = self.b[board_x][board_y]
            if not tile:
                continue
            x, y = board_x, board_y

            while self.can_move(x + dir_x, y + dir_y):
                self.b[x][y] = None
                x += dir_x
                y += dir_y
                self.b[x][y] = tile

            if self.can_merge(x + dir_x, y + dir_y, tile.number):
                self.b[x][y] = None
                x += dir_x
                y += dir_y
                self.remove_widget(self.b[x][y])
                self.b[x][y] = tile
                tile.number *= 2
                if tile.number == 2048:
                    print('You win the game.')
                tile.update_colors()

            if x == board_x and y == board_y:
                continue
            anim = Animation(pos=self.cell_pos(x, y), duration=0.25, transition='linear')
            if not self.moving:
                anim.on_complete = self.new_tile
                self.moving = True
            anim.start(tile)

    def resize(self, *args):
        self.cell_size = (.25 * (self.width - 5 * spacing),) * 2
        self.canvas.before.clear()
        with self.canvas.before:
            BorderImage(pos=self.pos, size=self.size, source='board.png')
            Color(*get_color_from_hex('ccc0b4'))
            for board_x, board_y in all_cells():
                BorderImage(pos=self.cell_pos(board_x, board_y), size=self.cell_size, source='cell.png')
        if not self.b:
            return

        for board_x, board_y in all_cells():
            tile = self.b[board_x][board_y]
            if tile:
                tile.resize(pos=self.cell_pos(board_x, board_y), size=self.cell_size)

    on_pos = resize
    on_size = resize

    def on_key_down(self, window, key, *args):
        if key in key_vectors:
            self.move(*key_vectors[key])

    def on_touch_up(self, touch):
        v = Vector(touch.pos) - Vector(touch.opos)
        if v.length < 20:
            return
        if abs(v.x) > abs(v.y):
            v.y = 0
        else:
            v.x = 0

        self.move(*v.normalize())


class GameApp(App):
    def on_start(self):
        board = self.root.ids.board
        board.reset()
        Window.bind(on_key_down=board.on_key_down)


if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('faf8ef')
    GameApp().run()
