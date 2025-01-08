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
            'covered_holes': -3,
        }
        self.first_held_piece = True  # Flag to track if this is the first piece
        self.hold_threshold = -15  # Threshold for holding the first piece

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
        """Generate all possible moves for the current piece and held piece if available"""
        if not self.game.current_piece:
            return []

        possible_moves = []
        pieces_to_try = [(self.game.current_piece.shape_name, False)]  # (shape_name, requires_hold)
        
        # Add held piece to possibilities if it exists and holding is allowed
        if self.game.held_piece and self.game.can_hold:
            pieces_to_try.append((self.game.held_piece.shape_name, True))

        board_width = self.game.grid.width

        # Try moves for both current piece and held piece
        for piece_shape, requires_hold in pieces_to_try:
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
                            'requires_hold': requires_hold,
                            'shape': piece_shape,
                            'type': 'normal'
                        }
                        
                        # Calculate score for this move
                        score = self.evaluate_position(resulting_board)
                        move['score'] = score
                        
                        possible_moves.append(move)

        return possible_moves

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
        
        # Check if we should hold the first piece
        if self.first_held_piece and best_move['score'] < self.hold_threshold and self.game.can_hold:
            self.first_held_piece = False  # Disable this check for future pieces
            best_move = {
                'rotation': 0,
                'x': 0,
                'y': 0,
                'requires_hold': True,
                'shape': self.game.current_piece.shape_name,
                'score': best_move['score'],
                'type': 'normal'
            }
            return best_move
        
        # Find the actual landing y position for the best move
        test_piece = Tetromino(best_move['shape'], self.game.grid)
        
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
