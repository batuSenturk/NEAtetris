# piece_generator.py

import random
from tetromino import Tetromino

class PieceGenerator:
    def __init__(self, grid):
        self.grid = grid
        self.bag = []
        self.next_pieces = []  # Queue of next pieces
        self.queue_size = 5    # Show next 5 pieces
        self.generate_new_bag()
        self.fill_queue()      # Fill the initial queue

    def generate_new_bag(self):
        self.bag = list('IOTSZJL')
        random.shuffle(self.bag)

    def get_next_piece_from_bag(self):
        if not self.bag:
            self.generate_new_bag()
        shape = self.bag.pop()
        return Tetromino(shape, self.grid)

    def fill_queue(self):
        """Fill the queue up to queue_size pieces"""
        while len(self.next_pieces) < self.queue_size:
            self.next_pieces.append(self.get_next_piece_from_bag())

    def get_next_piece(self):
        current_piece = self.next_pieces.pop(0)  # Get the first piece from queue
        self.fill_queue()  # Refill the queue
        return current_piece

    def preview_next_pieces(self):
        """Return list of next pieces"""
        return self.next_pieces
