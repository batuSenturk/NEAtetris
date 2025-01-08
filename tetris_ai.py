# tetris_ai.py

import copy
import numpy as np
from tetromino import Tetromino, SHAPES

class TetrisAI:
    def __init__(self, game):
        self.game = game
        # Initialize weights for different heuristics
        self.weights = {
            'aggregate_height': -2,
            'maximum_height': -2,
            'surface_variance': -1,
            'covered_holes': -4,
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
            'next_piece': self.game.next_pieces[0].shape_name if self.game.next_pieces else None,  # Get first piece from queue
            'score': self.game.score.score
        }
        return state

    def get_board_state(self):
        """Convert the game grid into a 2D binary array"""
        return [[1 if cell else 0 for cell in row] for row in self.game.grid.cells]

    def simulate_placement(self, piece_shape, rotation, x_pos):
        """Simulate placing a piece at a specific position and rotation"""
        try:
            # Create a copy of the current board
            board_copy = [row[:] for row in self.game.grid.cells]
            
            # Create a test piece
            test_piece = Tetromino(piece_shape, self.game.grid)
            
            # Apply rotation
            for _ in range(rotation):
                if not test_piece.rotate(use_wall_kicks=False):
                    return None
            
            # Set x position
            test_piece.x = x_pos
            
            # Find landing y position
            test_piece.y = 0  # Start from top
            while not self.game.grid.is_collision(test_piece):
                test_piece.y += 1
            test_piece.y -= 1  # Move back up one step
            
            # If piece is still above the board or in an invalid position, return None
            if test_piece.y < 0 or self.game.grid.is_collision(test_piece):
                return None
                
            # Place the piece on the board copy
            for block_x, block_y in test_piece.get_block_positions():
                if 0 <= block_y < len(board_copy) and 0 <= block_x < len(board_copy[0]):
                    board_copy[block_y][block_x] = 1
                else:
                    return None  # Return None if any part of the piece is out of bounds
                    
            return board_copy
            
        except Exception as e:
            print(f"Error in simulate_placement: {e}")
            return None

    def generate_possible_moves(self):
        """Generate all possible moves for the current piece"""
        if not self.game.current_piece:
            return []

        possible_moves = []
        piece_shape = self.game.current_piece.shape_name
        board_width = self.game.grid.width

        # Try all rotations (0 to 3)
        for rotation in range(4):
            # Try all horizontal positions
            for x in range(-2, board_width + 2):  # Include some buffer for rotations
                # Simulate the placement
                resulting_board = self.simulate_placement(piece_shape, rotation, x)
                
                if resulting_board is not None:
                    # Create move object
                    move = {
                        'rotation': rotation,
                        'x': x,
                        'y': None,  # Will be set when executing the move
                        'type': 'normal'
                    }
                    
                    # Calculate score for this move
                    score = self.evaluate_position(resulting_board)
                    move['score'] = score
                    
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
            print(''.join(['█' if cell == 1 else '.' for cell in row]))
        
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
            print(f"Score: {best_move['score']}")

            # Only simulate and print if the move is valid
            resulting_board = self.simulate_placement(
                self.game.current_piece.shape_name,
                best_move['rotation'],
                best_move['x']
            )
            if resulting_board is not None:
                print(f"Predicted Score: {self.evaluate_position(resulting_board)}")
            else:
                print("Warning: Could not simulate best move")

        # Print first few moves for reference
        print("\n=== Sample Moves ===")
        for i, move in enumerate(moves[:5]):
            print(f"Move {i + 1}: Rotation={move['rotation']}, X={move['x']}, Y={move['y']}, Type={move['type']}, Score={move['score']}")
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

        # Maximum Height
        maximum_height = max(heights) if heights else 0

        # Calculate remaining heuristics
        surface_variance = self.calculate_surface_variance(heights)
        covered_holes = self.calculate_covered_holes(board_state)

        return {
            'aggregate_height': aggregate_height,
            'maximum_height': maximum_height,
            'surface_variance': surface_variance,
            'covered_holes': covered_holes,
        }

    def calculate_surface_variance(self, heights):
        """Calculate how uneven the surface is"""
        if not heights:
            return 0
        avg_height = sum(heights) / len(heights)
        variance = sum((h - avg_height) ** 2 for h in heights) / len(heights)
        return variance

    def calculate_covered_holes(self, board_state):
        """Count holes that have blocks above them"""
        height = len(board_state)
        width = len(board_state[0])
        covered_holes = 0
        
        for row in range(height):
            for col in range(width):
                if board_state[row][col] == 0:
                    # Check if there are blocks above this empty cell
                    for above_row in range(row):
                        if board_state[above_row][col]:
                            covered_holes += 1
                            break
                        
        return covered_holes

    def evaluate_position(self, board_state):
        """Evaluate a board position using weighted heuristics"""
        heuristics = self.calculate_heuristics(board_state)
        score = sum(self.weights[key] * value for key, value in heuristics.items())
        return score

    def get_best_move(self):
        """Find the best move based on heuristics"""
        possible_moves = self.generate_possible_moves()
        
        if not possible_moves:
            return None
            
        # Sort moves by score and return the best one
        best_move = max(possible_moves, key=lambda x: x['score'])
        
        # Find the actual landing y position for the best move
        test_piece = Tetromino(self.game.current_piece.shape_name, self.game.grid)
        
        # Apply rotation
        for _ in range(best_move['rotation']):
            test_piece.rotate(use_wall_kicks=False)
            
        # Set x position and find y
        test_piece.x = best_move['x']
        test_piece.y = 0
        
        while not self.game.grid.is_collision(test_piece):
            test_piece.y += 1
        test_piece.y -= 1
        
        best_move['y'] = test_piece.y
        
        return best_move
