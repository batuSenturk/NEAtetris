# tetris_ai.py

import copy
import numpy as np
from tetromino import Tetromino, SHAPES

class TetrisAI:
    def __init__(self, game):
        self.game = game
        # Initialize weights for different heuristics
        self.weights = {
            'aggregate_height': -0.510066,
            'complete_lines': 0.760666,
            'holes': -0.35663,
            'bumpiness': -0.184483,
            'tspin_potential': 0.2,  # Custom weight for T-spin opportunities
        }

    def get_state_representation(self):
        """Get the current state of the game"""
        state = {
            'board': self.get_board_state(),
            'current_piece': {
                'shape': self.game.current_piece.shape_name,
                'x': self.game.current_piece.x,
                'y': self.game.current_piece.y,
                'rotation': self.game.current_piece.rotation_state
            },
            'next_piece': self.game.next_piece.shape_name if self.game.next_piece else None,
            'score': self.game.score.score
        }
        return state

    def get_board_state(self):
        """Convert the game grid into a 2D binary array"""
        return [[1 if cell else 0 for cell in row] for row in self.game.grid.cells]

    def generate_possible_moves(self):
        """Generate all possible moves for the current piece"""
        if not self.game.current_piece:
            return []

        possible_moves = []
        original_piece = self.game.current_piece

        # Try all rotations (0 to 3)
        for rotation in range(4):
            # Create a fresh test piece for each rotation
            test_piece = Tetromino(original_piece.shape_name, self.game.grid)
            test_piece.shape = copy.deepcopy(original_piece.shape)
            test_piece.rotation_state = 0

            # Start at the spawn position (y = -2 instead of -4)
            test_piece.y = -2  # Modified spawn height

            # Apply rotations without wall kicks
            rotation_successful = True
            for _ in range(rotation):
                if not test_piece.rotate(use_wall_kicks=False):
                    rotation_successful = False
                    break

            if not rotation_successful:
                continue

            # Try all horizontal positions
            for x in range(-2, self.game.grid.width + 2):
                # Create a fresh piece for each x position
                position_piece = Tetromino(original_piece.shape_name, self.game.grid)
                position_piece.shape = copy.deepcopy(test_piece.shape)
                position_piece.rotation_state = test_piece.rotation_state
                position_piece.x = x
                position_piece.y = -2  # Use same spawn height

                # If valid position, find landing position
                if not self.game.grid.is_collision(position_piece):
                    # Find landing position
                    while not self.game.grid.is_collision(position_piece):
                        position_piece.y += 1
                    position_piece.y -= 1

                    # Only add moves that result in valid positions
                    if position_piece.y >= -2:
                        move = {
                            'rotation': rotation,
                            'x': x,
                            'y': position_piece.y,
                            'type': 'normal'
                        }

                        if position_piece.shape_name == 'T':
                            move['type'] = 'potential_tspin'

                        possible_moves.append(move)

        return possible_moves

    def print_debug_info(self):
        """Print debug information about the current state and possible moves"""
        print("\n=== Current State ===")
        state = self.get_state_representation()
        print(f"Current Piece: {state['current_piece']['shape']}")
        print(f"Position: ({state['current_piece']['x']}, {state['current_piece']['y']})")
        print(f"Rotation: {state['current_piece']['rotation']}")
        print(f"Next Piece: {state['next_piece']}")

        print("\nBoard State:")
        for row in state['board']:
            print(''.join(['█' if cell else '.' for cell in row]))

        # Calculate and print heuristics for current board state
        heuristics = self.calculate_heuristics(state['board'])
        print("\n=== Current Heuristics ===")
        for key, value in heuristics.items():
            print(f"{key}: {value}")

        print("\n=== Possible Moves ===")
        moves = self.generate_possible_moves()
        print(f"Total possible moves: {len(moves)}")

        # Get and print the best move
        best_move = self.get_best_move()
        if best_move:
            print("\n=== Best Move ===")
            print(f"Rotation: {best_move['rotation']}")
            print(f"Position: ({best_move['x']}, {best_move['y']})")
            print(f"Type: {best_move['type']}")

            # Simulate and evaluate the best move
            resulting_board = self.simulate_move(best_move)
            score = self.evaluate_position(resulting_board)
            print(f"Predicted Score: {score}")

        # Print first few moves for reference
        print("\n=== Sample Moves ===")
        for i, move in enumerate(moves[:5]):
            print(f"Move {i + 1}: Rotation={move['rotation']}, X={move['x']}, Y={move['y']}, Type={move['type']}")
        if len(moves) > 5:
            print("... more moves available ...")

    def calculate_heuristics(self, board_state):
        """Calculate all heuristics for a given board state"""
        height = len(board_state)
        width = len(board_state[0])

        # Calculate column heights
        heights = [0] * width
        for col in range(width):
            for row in range(height):
                if board_state[row][col]:
                    heights[col] = height - row
                    break

        # Aggregate Height
        aggregate_height = sum(heights)

        # Complete Lines
        complete_lines = sum(1 for row in board_state if all(cell == 1 for cell in row))

        # Holes
        holes = 0
        for col in range(width):
            block_found = False
            for row in range(height):
                if board_state[row][col]:
                    block_found = True
                elif block_found:
                    holes += 1

        # Bumpiness (sum of differences between adjacent columns)
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(width-1))

        # T-spin potential (count T-shaped gaps with blocks above)
        tspin_potential = self.calculate_tspin_potential(board_state) if self.game.current_piece.shape_name == 'T' else 0

        return {
            'aggregate_height': aggregate_height,
            'complete_lines': complete_lines,
            'holes': holes,
            'bumpiness': bumpiness,
            'tspin_potential': tspin_potential
        }

    def calculate_tspin_potential(self, board_state):
        """Calculate potential T-spin opportunities in the board"""
        height = len(board_state)
        width = len(board_state[0])
        potential = 0

        # Look for T-spin opportunities (T-shaped gaps with blocks above)
        for row in range(1, height-1):
            for col in range(1, width-1):
                # Check for T-shaped gap
                if (not board_state[row][col] and  # Center empty
                    board_state[row-1][col] and    # Top filled
                    board_state[row][col-1] and    # Left filled
                    board_state[row][col+1]):      # Right filled
                    potential += 1

        return potential

    def evaluate_position(self, board_state):
        """Evaluate a board position using weighted heuristics"""
        heuristics = self.calculate_heuristics(board_state)
        score = sum(self.weights[key] * value for key, value in heuristics.items())
        return score

    def simulate_move(self, move):
        """Simulate a move and return the resulting board state"""
        # Create a deep copy of the current board
        board_copy = copy.deepcopy(self.game.grid.cells)
        piece_copy = Tetromino(self.game.current_piece.shape_name, self.game.grid)

        # Apply the move
        piece_copy.x = move['x']
        piece_copy.y = move['y']
        piece_copy.rotation_state = 0  # Reset rotation state
        piece_copy.shape = SHAPES[piece_copy.shape_name]  # Reset shape

        # Handle rotation with safety check
        target_rotation = move['rotation']
        current_rotation = piece_copy.rotation_state
        max_rotation_attempts = 4  # Prevent infinite loops

        while current_rotation != target_rotation and max_rotation_attempts > 0:
            if not piece_copy.rotate(use_wall_kicks=False):
                # If rotation fails, this move is invalid
                return None
            current_rotation = piece_copy.rotation_state
            max_rotation_attempts -= 1

        # If we couldn't achieve the desired rotation, this move is invalid
        if current_rotation != target_rotation:
            return None

        # Check for collision at the final position
        if self.game.grid.is_collision(piece_copy):
            return None

        # Lock the piece in place
        for x, y in piece_copy.get_block_positions():
            if 0 <= y < len(board_copy) and 0 <= x < len(board_copy[0]):
                board_copy[y][x] = 1

        return board_copy

    def get_best_move(self):
        """Find the best move based on heuristics"""
        possible_moves = self.generate_possible_moves()
        best_move = None
        best_score = float('-inf')

        for move in possible_moves:
            # Simulate the move
            resulting_board = self.simulate_move(move)
            # Skip invalid moves
            if resulting_board is None:
                continue

            # Evaluate the resulting position
            score = self.evaluate_position(resulting_board)

            # Update best move if this score is better
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
