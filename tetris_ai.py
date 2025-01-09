# tetris_ai.py

import copy
import numpy as np
from tetromino import Tetromino, SHAPES

class TetrisAI:
    def __init__(self, game):
        self.game = game
        # Weights strongly penalize height and holes
        self.weights = {
            'aggregate_height': -4.5,    
            'maximum_height': -3.5,      
            'surface_variance': -2.0,    
            'covered_holes': -7.5,       
        }
        self.first_held_piece = True  # Flag to track if this is the first piece
        self.hold_threshold = -15  # Threshold for holding the first piece

    def get_state_representation(self, grid, piece):
        """Get the current state of the game"""
        state = {
            'board': self.get_board_state(grid),
            'current_piece': {
                'shape': piece.shape_name,
                'x': piece.x,
                'y': piece.y,
                'rotation': piece.rotation_state
            },
            'next_piece': self.game.ai_next_pieces[0].shape_name if self.game.ai_next_pieces else None,
            'score': self.game.ai_score.score
        }
        return state

    def get_board_state(self, grid):
        """Convert the game grid into a 2D binary array"""
        return [[1 if cell else 0 for cell in row] for row in grid.cells]

    def simulate_placement(self, piece_shape, rotation, x_pos, grid):
        """Simulate placing a piece at a specific position and rotation"""
        try:
            # Create a copy of the current board
            board_copy = [row[:] for row in grid.cells]
            
            # Create a test piece
            test_piece = Tetromino(piece_shape, grid)
            
            # Apply rotation
            for _ in range(rotation):
                if not test_piece.rotate(use_wall_kicks=False):
                    return None
            
            # Set x position
            test_piece.x = x_pos
            
            # Find landing y position
            test_piece.y = 0  # Start from top
            while not grid.is_collision(test_piece):
                test_piece.y += 1
            test_piece.y -= 1  # Move back up one step
            
            # If piece is still above the board or in an invalid position, return None
            if test_piece.y < 0 or grid.is_collision(test_piece):
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

    def generate_possible_moves(self, grid, piece):
        """Generate all possible moves for the current piece and held piece if available"""
        if not piece:
            return []

        possible_moves = []
        pieces_to_try = [(piece.shape_name, False)]
        
        # Add held piece to possibilities if it exists and holding is allowed
        if self.game.ai_held_piece and self.game.can_hold:
            pieces_to_try.append((self.game.ai_held_piece.shape_name, True))

        board_width = grid.width

        for piece_shape, requires_hold in pieces_to_try:
            for rotation in range(4):
                for x in range(-2, board_width + 2):
                    resulting_board = self.simulate_placement(piece_shape, rotation, x, grid)
                    
                    if resulting_board is not None:
                        move = {
                            'rotation': rotation,
                            'x': x,
                            'y': None,
                            'requires_hold': requires_hold,
                            'shape': piece_shape,
                            'type': 'normal'
                        }
                        
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

        # Aggregate Height (with increased importance on higher stacks)
        aggregate_height = sum(h * 1.2 for h in heights)  # Progressive penalty for height

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
        """Count holes that have blocks above them with increased penalty for deep holes"""
        height = len(board_state)
        width = len(board_state[0])
        covered_holes = 0
        
        for col in range(width):
            found_block = False
            hole_depth = 0
            
            for row in range(height):
                if board_state[row][col]:
                    found_block = True
                elif found_block:
                    # Increase penalty for deeper holes
                    hole_depth += 1
                    covered_holes += hole_depth  # Progressive penalty

        return covered_holes

    def evaluate_position(self, board_state):
        """Evaluate a board position using weighted heuristics"""
        heuristics = self.calculate_heuristics(board_state)
        score = sum(self.weights[key] * value for key, value in heuristics.items())
        return score

    def get_best_move(self, grid, piece):
        """Find the best move based on heuristics"""
        if not piece:
            return None

        possible_moves = self.generate_possible_moves(grid, piece)
        
        if not possible_moves:
            return None
        
        # Sort moves by score and return the best one
        best_move = max(possible_moves, key=lambda x: x['score'])
        
        # Check if we should hold the first piece
        if self.first_held_piece and best_move['score'] < self.hold_threshold and self.game.can_hold:
            self.first_held_piece = False
            best_move = {
                'rotation': 0,
                'x': 0,
                'y': 0,
                'requires_hold': True,
                'shape': piece.shape_name,
                'score': best_move['score'],
                'type': 'normal'
            }
            return best_move
        
        # Find the actual landing y position for the best move
        test_piece = Tetromino(best_move['shape'], grid)
        
        # Apply rotation
        for _ in range(best_move['rotation']):
            test_piece.rotate(use_wall_kicks=False)
            
        # Set x position and find y
        test_piece.x = best_move['x']
        test_piece.y = 0
        
        while not grid.is_collision(test_piece):
            test_piece.y += 1
        test_piece.y -= 1
        
        best_move['y'] = test_piece.y
        
        return best_move
