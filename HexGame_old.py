import arcade
import arcade.gui
import collections
import queue
from math import pi as Pi, cos, sin, ceil


class HexGameWindow(arcade.Window):

    def __init__(self, width, height, name):
        super().__init__(width, height, name)
        self.game_is_over = False
        self.hexagon_list = [[Hexagon([])] * 11 for i in range(11)]
        self.win_checker = WinConditionChecker()
        self.ai = AI(-1)
        self.turn_controller = TurnController(1)
        self.set_location(500, 250)
        self.player_color = arcade.color.DARK_RED
        self.ai_color = arcade.color.DARK_BLUE
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box))
        arcade.set_background_color(arcade.color.DARK_BLUE)
        side_length = self.width / 32
        x_start = side_length
        y_start = self.height / 2
        for i in range(0, 11):
            for j in range(0, 11):
                self.hexagon_list[i][j] = Hexagon([((x_start + j * 1.5 * side_length) + side_length * cos(i * Pi / 3),
                                                    (y_start + j * side_length * sin(Pi / 3)) + side_length * sin(
                                                    i * Pi / 3)) for i in range(0, 6)])
            x_start = x_start + 1.5 * side_length
            y_start = y_start - side_length * sin(Pi / 3)

    def setup(self):
        self.game_is_over = False
        self.hexagon_list = [[Hexagon([])] * 11 for i in range(11)]
        self.win_checker = WinConditionChecker()
        self.ai = AI(-1)
        self.turn_controller = TurnController(1)
        self.set_location(500, 250)
        self.player_color = arcade.color.DARK_RED
        self.ai_color = arcade.color.DARK_BLUE
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box))
        arcade.set_background_color(arcade.color.DARK_BLUE)
        side_length = self.width / 32
        x_start = side_length
        y_start = self.height / 2
        for i in range(0, 11):
            for j in range(0, 11):
                self.hexagon_list[i][j] = Hexagon([((x_start + j * 1.5 * side_length) + side_length * cos(i * Pi / 3),
                                                    (y_start + j * side_length * sin(Pi / 3)) + side_length * sin(
                                                        i * Pi / 3)) for i in range(0, 6)])
            x_start = x_start + 1.5 * side_length
            y_start = y_start - side_length * sin(Pi / 3)

    def create_game_finish_message(self, win_player):
        player_name = "p1" if win_player == 1 else "p2"
        finish_message = arcade.gui.UIMessageBox(
            width=300,
            height=100,
            message_text="{0} wins".format(player_name),
            callback=self.finish_game,
            buttons=["Finish", "Restart"]
        )
        self.manager.add(finish_message)

    def finish_game(self, button_text):
        self.setup() if button_text == "Restart" else self.close()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrtb_rectangle_filled(0, self.width/2, self.height/2, 0, arcade.color.DARK_RED)
        arcade.draw_lrtb_rectangle_filled(self.width/2, self.width, self.height, self.height/2, arcade.color.DARK_RED)
        for i in range(0, 11):
            for j in range(0, 11):
                self.hexagon_list[i][j].fill()
                self.hexagon_list[i][j].draw_outline()
        self.manager.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.game_is_over:
            return None
        click_is_inside = False
        hex_num_x = -1
        hex_num_y = -1
        if button == arcade.MOUSE_BUTTON_LEFT and self.turn_controller.current_turn == 1:
            for i in range(11):
                for j in range(11):
                    if self.hexagon_list[i][j].point_inside_hexagon(x, y):
                        if not self.hexagon_list[i][j].can_be_filled():
                            return
                        click_is_inside = True
                        hex_num_x = i
                        hex_num_y = j
                        break
            if click_is_inside:
                self.hexagon_list[hex_num_x][hex_num_y].fill_color = self.player_color
                if self.win_checker.paint_point(hex_num_x, hex_num_y, 1):
                    self.create_game_finish_message(1)
                    self.game_is_over = True
                if not self.game_is_over:
                    self.draw_ai_turn()
                    for i in range(11):
                        for j in range(11):
                            print('%2d' % self.win_checker.board[i][j].color, end='')
                        print('     ', end='')
                        for j in range(11):
                            print('%2d' % self.win_checker.board[i][j].way, end='')
                        print()
                    print()

    def draw_ai_turn(self):
        self.turn_controller.ai_turn()
        ai_turn = self.ai.make_turn(self.win_checker.board)
        self.hexagon_list[ai_turn.x][ai_turn.y].fill_color = self.ai_color
        if self.win_checker.paint_point(ai_turn.x, ai_turn.y, -1):
            self.create_game_finish_message(-1)
            self.game_is_over = True
        if not self.game_is_over:
            self.turn_controller.player_turn()


class Hexagon:

    fill_color = arcade.color.WHITE
    outline_color = arcade.color.BLACK
    outline_width = 5

    def __init__(self, points):
        self.points = points

    def can_be_filled(self):
        return self.fill_color == arcade.color.WHITE

    def fill(self):
        arcade.draw_polygon_filled(self.points, self.fill_color)

    def draw_outline(self):
        arcade.draw_polygon_outline(self.points, self.outline_color, self.outline_width)

    def point_inside_hexagon(self, x, y):
        n = len(self.points)
        inside = False
        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside


class Way:

    def __init__(self, points):
        self.points = points
        self.contains_start = False
        self.contains_end = False

    def is_complete(self):
        return self.contains_start and self.contains_end


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = 0
        self.way = 0

    def __gt__(self, other):
        if self.color == 1:
            return self.y > other.y
        return self.x > other.x

    def __lt__(self, other):
        if self.color == 1:
            return self.y < other.y
        return self.x < other.x

    def __eq__(self, other):
        return (self.color == other.color) and (self.x == other.x) and (self.y == other.y)

    def __sub__(self, other):
        if self.color == 1:
            return self.y - other.y
        return self.x - other.x

    def __str__(self):
        return str(self.x) + ' ' + str(self.y)

    def is_start(self):
        if self.color == 1:
            return self.y == 0
        return self.x == 0

    def is_end(self):
        if self.color == 1:
            return self.y == 10
        return self.x == 10

    def distance_to_border(self, color):
        if color == 1:
            return min(self.y, 10 - self.y)
        if color == -1:
            return min(self.x, 10 - self.x)

    def distance_to_mid(self, color):
        if color == 1:
            return abs(self.x - 5)
        if color == -1:
            return abs(self.y - 5)

    def can_go_further(self, board, attr):
        if getattr(self, attr) == 10:
            return True
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (not i == j) and (-1 < self.x + i < 11) and (-1 < self.y + j < 11) \
                        and (board[self.x + i][self.y + j].color == 0) \
                        and (getattr(self, attr) < getattr(board[self.x + i][self.y + j], attr)):
                    print(self.x, self.y, "->", self.x + i, self.y + j)
                    return True
        return False

    def can_go_back(self, board, attr):
        if getattr(self, attr) == 0:
            return True
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (not i == j) and (-1 < self.x + i < 11) and (-1 < self.y + j < 11) \
                        and (board[self.x + i][self.y + j].color == 0) \
                        and (getattr(self, attr) > getattr(board[self.x + i][self.y + j], attr)):
                    return True
        return False


class WinConditionChecker:

    def __init__(self):
        self.board = [[Point(0, 0)] * 11 for i in range(11)]
        for i in range(11):
            for j in range(11):
                self.board[i][j] = Point(i, j)
        self.ways = collections.OrderedDict()
        self.player_current_way_num = 0
        self.ai_current_way_num = 0

    def add_point_to_way(self, point, way_number):
        point.way = way_number
        if self.ways.get(way_number) is not None:
            self.ways[way_number].points.append((point.x, point.y))
        else:
            self.ways[way_number] = Way([(point.x, point.y)])
        if point.is_start():
            self.ways[way_number].contains_start = True
        elif point.is_end():
            self.ways[way_number].contains_end = True
        return self.ways[way_number].is_complete()

    def check_way(self, point):
        ways_to_merge = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (not i == j) and (-1 < point.x+i < 11) and (-1 < point.y+j < 11):
                    if self.board[point.x+i][point.y+j].color == point.color:
                        ways_to_merge.append(self.board[point.x+i][point.y+j].way)
        ways_to_merge_set = set(ways_to_merge)
        if len(ways_to_merge_set) <= 1:
            if len(ways_to_merge_set) == 0:
                if point.color == 1:
                    self.player_current_way_num += 1
                    way_to_set = self.player_current_way_num
                else:
                    self.ai_current_way_num -= 1
                    way_to_set = self.ai_current_way_num
            else:
                way_to_set = ways_to_merge[0]
            return self.add_point_to_way(point, way_to_set)
        else:
            way_to_set = ways_to_merge[0]
            return self.add_point_to_way(point, way_to_set) or self.merge_ways(ways_to_merge_set)

    def merge_ways(self, ways_to_merge):
        merged_num = ways_to_merge.pop()
        merged_way = self.ways[merged_num]
        for way_number in ways_to_merge:
            merged_way.points = [*merged_way.points, *(self.ways[way_number].points)]
            merged_way.contains_start = merged_way.contains_start or self.ways[way_number].contains_start
            merged_way.contains_end = merged_way.contains_end or self.ways[way_number].contains_end
            self.ways.pop(way_number)
        for point in merged_way.points:
            self.board[point[0]][point[1]].way = merged_num
        return merged_way.is_complete()

    def paint_point(self, x, y, color):
        self.board[x][y].color = color
        return self.check_way(self.board[x][y])


class AI:

    def __init__(self, ai_color):
        self.color = ai_color

    @staticmethod
    def component_length(component, color):
        coord_attr = "y" if color == 1 else "x"
        min_value = 12
        max_value = -1
        for point in component:
            current_coord = getattr(point, coord_attr)
            if current_coord < min_value:
                min_value = current_coord
            if current_coord > max_value:
                max_value = current_coord
        return max_value - min_value

    def make_turn(self, board):
        turn_not_decided = True
        p1_ways, p2_ways = self.find_ways(board)
        p1_ways.sort(key=lambda comp: comp[2].y - comp[1].y, reverse=True)
        p2_ways.sort(key=lambda comp: comp[2].x - comp[1].x, reverse=True)
        p1_index = 0
        p2_index = 0
        p1_out_of_ways = False if p1_ways else True
        if not p1_out_of_ways:
            p1_way = p1_ways[p1_index]
        p2_out_of_ways = False if p2_ways else True
        if not p2_out_of_ways:
            p2_way = p2_ways[p2_index]
        potential_turn = Point(-1, -1)
        while turn_not_decided:
            if p1_out_of_ways or ((not p2_out_of_ways) and (p2_way[2] - p2_way[1] >= p1_way[2] - p1_way[1])):
                potential_turn = AI.make_offensive_play(p2_way, board)
                if potential_turn == Point(-2, -2):
                    print("offensive not found")
                    p2_index += 1
                    try:
                        p2_way = p2_ways[p2_index]
                    except IndexError:
                        p2_out_of_ways = True
                else:
                    turn_not_decided = False
            else:
                potential_turn = AI.make_defensive_play(p1_way, board)
                if potential_turn == Point(-2, -2):
                    print("defensive not found")
                    p1_index += 1
                    try:
                        p1_way = p1_ways[p1_index]
                    except IndexError:
                        p1_out_of_ways = True
                else:
                    turn_not_decided = False
        return potential_turn

    @staticmethod
    def make_offensive_play(way, board):
        min_to_mid = 12
        current_diff_x = 1
        final_point = Point(-2, -2)
        for point in way[0]:
            direct_found = False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (not i == j) and (-1 < point.x + i < 11) and (-1 < point.y + j < 11)\
                            and (board[point.x + i][point.y + j].color == 0):
                        potential_point = board[point.x + i][point.y + j]
                        if (potential_point.x - way[2].x > current_diff_x) \
                                or (way[1].x - potential_point.x > current_diff_x):
                            final_point = potential_point
                            min_to_mid = final_point.distance_to_mid(1)
                            current_diff_x = max(potential_point.x - way[2].x, way[1].x - potential_point.x)
                        elif (potential_point.x - way[2].x == current_diff_x) \
                                or (way[1].x - potential_point.x == current_diff_x):
                            if (potential_point.distance_to_mid(-1) < min_to_mid) and (not direct_found):
                                final_point = potential_point
                                min_to_mid = final_point.distance_to_mid(-1)
                                current_diff_x = max(potential_point.x - way[2].x, way[1].x - potential_point.x)
                            if potential_point.y == point.y:
                                final_point = potential_point
                                min_to_mid = final_point.distance_to_mid(-1)
                                current_diff_x = max(potential_point.x - way[2].x, way[1].x - potential_point.x)
                                direct_found = True
        print(final_point.x, final_point.y, "offensive")
        return final_point

    @staticmethod
    def make_defensive_play(way, board):
        min_to_mid = 12
        current_diff_y = 1
        final_point = Point(-2, -2)
        for point in way[0]:
            direct_found = False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (not i == j) and (-1 < point.x + i < 11) and (-1 < point.y + j < 11)\
                            and (board[point.x + i][point.y + j].color == 0):
                        potential_point = board[point.x + i][point.y + j]
                        if (potential_point.y - way[2].y > current_diff_y)\
                                or (way[1].y - potential_point.y > current_diff_y):
                            final_point = potential_point
                            min_to_mid = final_point.distance_to_mid(1)
                            current_diff_y = max(potential_point.y - way[2].y, way[1].y - potential_point.y)
                        elif (potential_point.y - way[2].y == current_diff_y)\
                                or (way[1].y - potential_point.y == current_diff_y):
                            if (potential_point.distance_to_mid(1) < min_to_mid) and (not direct_found):
                                final_point = potential_point
                                min_to_mid = final_point.distance_to_mid(1)
                                current_diff_y = max(potential_point.y - way[2].y, way[1].y - potential_point.y)
                            if potential_point.x == point.x:
                                final_point = potential_point
                                min_to_mid = final_point.distance_to_mid(1)
                                current_diff_y = max(potential_point.y - way[2].y, way[1].y - potential_point.y)
                                direct_found = True
        print(final_point.x, final_point.y, "defensive")
        return final_point

    def find_ways(self, board):
        visited = [[0] * 11 for i in range(11)]
        player1_ways = []
        player2_ways = []
        for a in range(11):
            for b in range(11):
                if (board[a][b].color == 0) or (visited[a][b] == 1):
                    continue
                current_color = board[a][b].color
                coord_attr = "y" if current_color == 1 else "x"
                min_value = 12
                min_point = Point(-3, -3)
                max_value = -1
                max_point = Point(-3, -3)
                q = queue.SimpleQueue()
                q.put(board[a][b])
                point_list = []
                while not q.empty():
                    current_point = q.get()
                    visited[current_point.x][current_point.y] = 1
                    point_list.append(current_point)
                    current_coord = getattr(current_point, coord_attr)
                    if (current_coord < min_value) and (current_point.can_go_back(board, coord_attr)):
                        min_value = current_coord
                        min_point = current_point
                    if (current_coord > max_value) and (current_point.can_go_further(board, coord_attr)):
                        max_value = current_coord
                        max_point = current_point
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if (not i == j) and (-1 < current_point.x + i < 11) and (-1 < current_point.y + j < 11)\
                                    and (visited[current_point.x + i][current_point.y + j] == 0)\
                                    and (board[current_point.x + i][current_point.y + j].color == current_point.color):
                                q.put(board[current_point.x + i][current_point.y + j])
                                visited[current_point.x + i][current_point.y + j] = 1
                if (not min_point.y == -3) and (not max_point.y == -3):
                    if current_color == 1:
                        player1_ways.append((point_list, min_point, max_point, coord_attr))
                    else:
                        player2_ways.append((point_list, min_point, max_point, coord_attr))
                for way in player1_ways:
                    print(*way[0], "||", way[1], "||", way[2])
                for way in player2_ways:
                    print(*way[0], "||", way[1], "||", way[2])
        return player1_ways, player2_ways


class TurnController:

    def __init__(self, first_turn):
        self.current_turn = first_turn

    def ai_turn(self):
        self.current_turn = -1

    def player_turn(self):
        self.current_turn = 1


def start_game():
    HexGameWindow(1056, ceil(1056 * sin(Pi/3)*(22/32)), 'HexGame')
    arcade.run()


if __name__ == '__main__':
    start_game()
