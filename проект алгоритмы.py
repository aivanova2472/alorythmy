import pygame
import numpy as np
import itertools
import sys
import networkx as nx
import collections
from pygame import gfxdraw



BOARD_BROWN = (199, 105, 42)
BOARD_WIDTH = 760
BOARD_BORDER = 75
STONE_RADIUS = 22
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (BOARD_BORDER, 20)
SCORE_POS = (BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER + 30)
DOT_RADIUS = 4


def make_grid(size):
    start_points, end_points = [], []
    # начальные точки по вертикали
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))
    # начальные точки по горизонтали
    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))
    # конечные точки по вертикали
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))
    # конечные точки по горизонтали
    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))
    return (start_points, end_points)



def xy_to_colrow(x, y, size):
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row


def colrow_to_xy(col, row, size):
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y


def has_no_liberties(board, group):
    for x, y in group:
        if x > 0 and board[x - 1, y] == 0:
            return False
        if y > 0 and board[x, y - 1] == 0:
            return False
        if x < board.shape[0] - 1 and board[x + 1, y] == 0:
            return False
        if y < board.shape[0] - 1 and board[x, y + 1] == 0:
            return False
    return True


def get_stone_groups(board, color):
    size = board.shape[0]
    color_code = 1 if color == "black" else 2
    xs, ys = np.where(board == color_code)
    graph = nx.grid_graph(dim=[size, size])
    stones = set(zip(xs, ys))
    all_spaces = set(itertools.product(range(size), range(size)))
    stones_to_remove = all_spaces - stones
    graph.remove_nodes_from(stones_to_remove)
    return nx.connected_components(graph)

def is_valid_move(col, row, board):
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False
    return board[col, row] == 0


class Game:
    def __init__(self, size):
        self.board = np.zeros((size, size))
        self.size = size
        self.black_turn = True
        self.prisoners = collections.defaultdict(int)
        self.start_points, self.end_points = make_grid(self.size)

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.ZOINK = pygame.mixer.Sound("wav_zoink.wav")
        self.CLICK = pygame.mixer.Sound("wav_click.wav")
        self.font = pygame.font.SysFont("arial", 30)

    def clear_screen(self):
        # интерфейс доски
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)
        guide_dots = [3, self.size // 2, self.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)
        pygame.display.flip()

    def pass_move(self):
        self.black_turn = not self.black_turn
        self.draw()

    def handle_click(self):
        x, y = pygame.mouse.get_pos()
        col, row = xy_to_colrow(x, y, self.size)
        if not is_valid_move(col, row, self.board):
            self.ZOINK.play()
            return
        self.board[col, row] = 1 if self.black_turn else 2
        self_color = "black" if self.black_turn else "white"
        other_color = "white" if self.black_turn else "black"
        capture_happened = False
        for group in list(get_stone_groups(self.board, other_color)):
            if has_no_liberties(self.board, group):
                capture_happened = True
                for i, j in group:
                    self.board[i, j] = 0
                self.prisoners[self_color] += len(group)
        if not capture_happened:
            group = None
            for group in get_stone_groups(self.board, self_color):
                if (col, row) in group:
                    break
            if has_no_liberties(self.board, group):
                self.ZOINK.play()
                self.board[col, row] = 0
                return
        self.CLICK.play()
        self.black_turn = not self.black_turn
        self.draw()

    def draw(self):
        # рисуем камни
        self.clear_screen()
        for col, row in zip(*np.where(self.board == 1)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, BLACK)
        for col, row in zip(*np.where(self.board == 2)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, WHITE)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, WHITE)
        # информация об очках
        score_msg = (
                f"Очки чёрных: {self.prisoners['black']}"
                + f"     Очки белых: {self.prisoners['white']}"
        )
        txt = self.font.render(score_msg, True, BLACK)
        self.screen.blit(txt, SCORE_POS)
        turn_msg = (
            f"{'Черные' if self.black_turn else 'Белые'} ходят. "
            + "Чтобы пропустить ход нажмите Р"
        )
        txt = self.font.render(turn_msg, True, BLACK)
        self.screen.blit(txt, TURN_POS)
        pygame.display.flip()

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_click()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.pass_move()


if __name__ == "__main__":
    g = Game(size=19)
    g.init_pygame()
    g.clear_screen()
    g.draw()
    while True:
        g.update()
        pygame.time.wait(100)