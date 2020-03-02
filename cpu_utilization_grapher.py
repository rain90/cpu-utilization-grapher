import os
import platform
import random
import time

import psutil


class BarDiagramGraphicalElement:
    HORIZONTAL_DIVIDER = "¯"
    BAR_POINT = "#"


class CharacterCanvas:
    def __init__(self, width=1, height=1, background_char=" "):
        self._width = width
        self._height = height
        self._background_char = str(background_char)
        self._canvas = [[self._background_char for y in range(height)] for x in range(width)]

    def _get_transposed_matrix_datastructure(self, matrix: list):
        matrix_width = len(matrix)
        matrix_height = len(matrix[0])
        return [[matrix[x][y] for x in range(matrix_width)] for y in range(matrix_height)]

    def _process_list_for_replace(self, input_list: list):
        return [str(i) for i in input_list]

    def _update_canvas_size_variables(self):
        self._width = len(self._canvas)
        self._height = len(self._canvas[0])

    def print(self):
        transposed_canvas_datastructure = self._get_transposed_matrix_datastructure(self._canvas)
        for row in transposed_canvas_datastructure:
            print("".join(row))

    def replace_row_at_index(self, row: list, index: int):
        row_max_width = self._width if self._width <= len(row) else len(row)
        row = self._process_list_for_replace(row)
        temp_canvas = self._get_transposed_matrix_datastructure(self._canvas)
        for i in range(row_max_width):
            temp_canvas[index][i] = row[i]
        self._canvas = self._get_transposed_matrix_datastructure(temp_canvas)

    def replace_column_at_index(self, column: list, index: int):
        column_max_height = self._height if self._height <= len(column) else len(column)
        column = self._process_list_for_replace(column)
        for i in range(column_max_height):
            self._canvas[index][i] = column[i]

    def set_character(self, x: int, y: int, character: str):
        self._canvas[x][y] = character

    def set_canvas_state(self, new_canvas: list):
        self._canvas = new_canvas
        self._update_canvas_size_variables()

    def apply_to_all_characters(self, fun):
        result = []
        for column in self._canvas:
            result.append(list(map(fun, column)))
        self._canvas = result


class BarDiagram:
    def __init__(self):
        self._columns = []

    def _create_horizontal_divider(self):
        horizontal_divider = []
        for _ in range(len(self._columns)):
            horizontal_divider.append(BarDiagramGraphicalElement.HORIZONTAL_DIVIDER)
        return horizontal_divider

    def _get_transposed_matrix_datastructure(self, matrix: list):
        matrix_width = len(matrix)
        matrix_height = len(matrix[0])
        return [[matrix[x][y] for x in range(matrix_width)] for y in range(matrix_height)]

    def _diagram_height(self):
        diagram_height = 0
        for column in self._columns:
            diagram_height = len(column) if len(column) > diagram_height else diagram_height
        return diagram_height

    def _get_padded_diagram(self, height):
        padded_diagram = []
        diagram_current_height = self._diagram_height()
        diagram_height = height if height > diagram_current_height else diagram_current_height
        for column in self._columns:
            paddings_to_add = diagram_height - len(column)
            padded_column = [" "] * paddings_to_add + column
            padded_diagram.append(padded_column)
        return padded_diagram

    def _create_column(self, column_height, bar_point_character):
        return int(column_height) * [bar_point_character]

    def add_column_to_right(self, column_height=0,
                            bar_point_character=BarDiagramGraphicalElement.BAR_POINT):
        column = self._create_column(column_height, bar_point_character)
        self._columns.append(column)

    def add_column_to_left(self, column_height=0,
                           bar_point_character=BarDiagramGraphicalElement.BAR_POINT):
        column = self._create_column(column_height, bar_point_character)
        self._columns = column + self._columns

    def remove_column_from_right(self):
        self._columns.pop()

    def remove_column_from_left(self):
        self._columns = self._columns[1::]

    def set_diagram_state(self, column_heights: list,
                          bar_point_character=BarDiagramGraphicalElement.BAR_POINT):
        self.empty_diagram()
        for column_height in column_heights:
            self.add_column_to_right(column_height, bar_point_character)

    def empty_diagram(self):
        self._columns = []

    def get_formatted_bar_diagram(self, height):
        horizontal_divider = self._create_horizontal_divider()
        padded_diagram = self._get_padded_diagram(height)
        transposed_diagram = self._get_transposed_matrix_datastructure(padded_diagram)
        transposed_diagram.append(horizontal_divider)
        return self._get_transposed_matrix_datastructure(transposed_diagram)


class ListLog:
    def __init__(self, max_history: int):
        self._log_data = []
        self._max_history = max_history

    def _reduce_history(self):
        if(len(self._log_data) > self._max_history):
            self._log_data = self._log_data[1::]

    def clear_log(self):
        self._log_data = []

    def add_log(self, log_data):
        self._log_data.append(log_data)
        self._reduce_history()

    def get_logs(self, amount=0):
        return self._log_data[-amount::]


class CPUUtilityGrapher:
    def __init__(self, width, height, sleep_interval):
        self._width = width
        self._height = height
        self._sleep_interval = sleep_interval
        self._platform = self._get_platform()

        self._canvas = CharacterCanvas(self._width)
        self._cpu_log = ListLog(self._width)
        self._bar_diagram = BarDiagram()

    def _get_platform(self):
        return platform.system()

    def _clear_terminal(self):
        if(self._platform == "Windows"):
            os.system("cls")
        elif(self._platform == "Linux"):
            os.system("clear")

    def _setup_cpu_log(self):
        for _ in range(self._width):
            self._cpu_log.add_log(0)

    def _parse_cpu_percent(self, cpu_utility_percent):
        return int((self._height / 100) * cpu_utility_percent)

    def _get_cpu_utility_percent(self):
        cpu_utility_percent = psutil.cpu_percent()
        return self._parse_cpu_percent(cpu_utility_percent)

    def _start(self):
        while(True):
            self._clear_terminal()
            self._cpu_log.add_log(self._get_cpu_utility_percent())
            self._bar_diagram.set_diagram_state(self._cpu_log.get_logs())
            self._canvas.set_canvas_state(
                self._bar_diagram.get_formatted_bar_diagram(self._height))
            self._canvas.print()
            print("Press Ctrl-C to stop")
            time.sleep(self._sleep_interval)

    def start(self):
        self._setup_cpu_log()
        try:
            self._start()
        except KeyboardInterrupt:
            print()


cpu_utility_graph = CPUUtilityGrapher(60, 20, 1)
cpu_utility_graph.start()
