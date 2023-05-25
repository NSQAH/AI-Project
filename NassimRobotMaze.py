import tkinter as tk
from queue import PriorityQueue
import random

class MazeSolverGUI:
    def __init__(self, maze, cell_size=40, movement_delay=500):
        self.maze = maze
        self.num_rows = len(maze)
        self.num_cols = len(maze[0])
        self.cell_size = cell_size
        self.movement_delay = movement_delay
        self.start_row, self.start_col = self.find_start_position()
        self.goal_row, self.goal_col = self.find_goal_position()
        self.window = None
        self.canvas = None
        self.rectangles = {}
        self.robot = None
        self.path = []
        self.current_position = 0
        self.is_robot_moving = False

    def find_start_position(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.maze[row][col] == 'S':
                    return row, col
        return None

    def find_goal_position(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.maze[row][col] == 'E':
                    return row, col
        return None

    def create_gui(self):
        self.window = tk.Tk()
        self.window.title("Maze Solver")

        self.canvas = tk.Canvas(self.window, width=self.num_cols * self.cell_size,
                                height=self.num_rows * self.cell_size)

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if self.maze[row][col] == '#':
                    self.rectangles[(row, col)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')
                elif self.maze[row][col] == 'S':
                    self.rectangles[(row, col)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill='green')
                elif self.maze[row][col] == 'E':
                    self.rectangles[(row, col)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill='red')
                else:
                    self.rectangles[(row, col)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill='white')

        self.canvas.pack()

        self.robot = self.canvas.create_text(
            self.start_col * self.cell_size + self.cell_size // 2,
            self.start_row * self.cell_size + self.cell_size // 2,
            text='R', fill='blue', font=('Arial', 14, 'bold')
        )

    def solve_maze(self):
        start_node = (self.start_row, self.start_col)
        goal_node = (self.goal_row, self.goal_col)

        if not goal_node:
            print("No goal position found in the maze.")
            return

        frontier = PriorityQueue()
        frontier.put((0, start_node))
        came_from = {}
        cost_so_far = {}
        came_from[start_node] = None
        cost_so_far[start_node] = 0

        while not frontier.empty():
            current_node = frontier.get()[1]

            if current_node == goal_node:
                break

            for neighbor in self.get_neighbors(current_node):
                new_cost = cost_so_far[current_node] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, goal_node)
                    frontier.put((priority, neighbor))
                    came_from[neighbor] = current_node

        if goal_node not in came_from:
            print("No path found from the starting position to the goal position.")
            self.is_robot_moving = False
            return

        self.path = self.reconstruct_path(came_from, start_node, goal_node)

    def get_neighbors(self, node):
        row, col = node
        neighbors = []

        if row > 0 and self.maze[row - 1][col] != '#':
            neighbors.append((row - 1, col))  # Up
        if row < self.num_rows - 1 and self.maze[row + 1][col] != '#':
            neighbors.append((row + 1, col))  # Down
        if col > 0 and self.maze[row][col - 1] != '#':
            neighbors.append((row, col - 1))  # Left
        if col < self.num_cols - 1 and self.maze[row][col + 1] != '#':
            neighbors.append((row, col + 1))  # Right

        return neighbors

    def heuristic(self, node, goal_node):
        return abs(node[0] - goal_node[0]) + abs(node[1] - goal_node[1])

    def reconstruct_path(self, came_from, start_node, goal_node):
        current_node = goal_node
        path = [current_node]

        while current_node != start_node:
            current_node = came_from[current_node]
            path.append(current_node)

        path.reverse()
        return path

    def move_robot(self):
        if self.is_robot_moving and self.current_position < len(self.path) - 1:
            self.current_position += 1
            new_row, new_col = self.path[self.current_position]
            new_x = new_col * self.cell_size + self.cell_size // 2
            new_y = new_row * self.cell_size + self.cell_size // 2
            self.canvas.coords(self.robot, new_x, new_y)
            self.window.after(self.movement_delay, self.move_robot)
        elif self.is_robot_moving and self.current_position == len(self.path) - 1:
            self.is_robot_moving = False

    def start_robot(self):
        if not self.is_robot_moving:
            self.is_robot_moving = True
            self.move_robot()

    def pause_robot(self):
        self.is_robot_moving = False

    def reset_maze(self):
        self.current_position = 0
        self.is_robot_moving = False
        self.canvas.coords(self.robot,
                           self.start_col * self.cell_size + self.cell_size // 2,
                           self.start_row * self.cell_size + self.cell_size // 2)

    def regenerate_maze(self):
        self.maze = self.generate_random_maze()
        self.start_row, self.start_col = self.find_start_position()
        self.goal_row, self.goal_col = self.find_goal_position()
        self.reset_maze()
        self.update_gui()
        self.solve_maze()

        # Check if the robot is surrounded by black boxes
        if self.is_surrounded_by_black_boxes():
            self.is_robot_moving = False

    def generate_random_maze(self):
        # Generate a new random maze
        maze = [['#' if random.random() < 0.3 else ' ' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        maze[self.start_row][self.start_col] = 'S'
        goal_row, goal_col = random.randint(0, self.num_rows - 1), random.randint(0, self.num_cols - 1)
        maze[goal_row][goal_col] = 'E'
        return maze

    def update_gui(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                rectangle = self.rectangles[(row, col)]
                if self.maze[row][col] == '#':
                    self.canvas.itemconfig(rectangle, fill='black')
                elif self.maze[row][col] == 'S':
                    self.canvas.itemconfig(rectangle, fill='green')
                elif self.maze[row][col] == 'E':
                    self.canvas.itemconfig(rectangle, fill='red')
                else:
                    self.canvas.itemconfig(rectangle, fill='white')

    def is_surrounded_by_black_boxes(self):
        row, col = self.path[self.current_position]
        if (row > 0 and self.maze[row - 1][col] == '#') and \
                (row < self.num_rows - 1 and self.maze[row + 1][col] == '#') and \
                (col > 0 and self.maze[row][col - 1] == '#') and \
                (col < self.num_cols - 1 and self.maze[row][col + 1] == '#'):
            return True
        return False

    def run(self):
        self.create_gui()

        start_button = tk.Button(self.window, text="Start", command=self.start_robot)
        start_button.pack(side=tk.LEFT)

        pause_button = tk.Button(self.window, text="Pause", command=self.pause_robot)
        pause_button.pack(side=tk.LEFT)

        reset_button = tk.Button(self.window, text="Reset", command=self.reset_maze)
        reset_button.pack(side=tk.LEFT)

        regenerate_button = tk.Button(self.window, text="Regenerate Maze", command=self.regenerate_maze)
        regenerate_button.pack(side=tk.LEFT)

        self.solve_maze()

        self.window.mainloop()

# Define the maze as a 2D list
maze = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', 'S', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
    ['#', '#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', ' ', '#', ' ', '#'],
    ['#', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '#', ' ', '#', ' ', '#'],
    ['#', '#', ' ', '#', '#', ' ', '#', '#', '#', '#', '#', ' ', '#', '#', '#', '#', ' ', '#', ' ', '#'],
    ['#', '#', ' ', '#', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
    ['#', '#', ' ', '#', ' ', '#', '#', ' ', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', '#'],
    ['#', '#', ' ', '#', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', '#'],
    ['#', '#', ' ', ' ', ' ', '#', '#', ' ', '#', ' ', ' ', ' ', '#', '#', '#', ' ', '#', ' ', ' ', '#'],
    ['#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', '#', '#', ' ', ' ', '#', ' ', '#', '#', ' ', '#'],
    ['#', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', '#'],
    ['#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', '#'],
    ['#', '#', ' ', '#', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', '#'],
    ['#', '#', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', ' ', '#', '#'],
    ['#', '#', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', '#', ' ', '#', '#'],
    ['#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', ' ', 'E', '#'],
    ['#', '#', ' ', '#', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '#', ' ', '#'],
    ['#', '#', ' ', '#', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', '#']
]

maze_solver = MazeSolverGUI(maze)
maze_solver.run()
