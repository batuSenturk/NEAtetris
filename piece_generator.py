# piece_generator.py

import random
from tetromino import Tetromino

class PieceGenerator:
    def __init__(self, grid):
        self.grid = grid
        self.bag = []
        self.generate_new_bag()
        self.next_piece = self.get_next_piece_from_bag()

    def generate_new_bag(self):
        self.bag = list('IOTSZJL')
        random.shuffle(self.bag)

    def get_next_piece_from_bag(self):
        if not self.bag:
            self.generate_new_bag()
        shape = self.bag.pop()
        return Tetromino(shape, self.grid)

    def get_next_piece(self):
        current_piece = self.next_piece
        self.next_piece = self.get_next_piece_from_bag()
        return current_piece

    def preview_next_piece(self):
        return self.next_piece
