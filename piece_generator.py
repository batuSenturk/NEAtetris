# piece_generator.py

import random
from tetromino import Tetromino

class Queue:
    """A simple queue implementation with basic operations"""
    def __init__(self, capacity=None):
        self.capacity = capacity
        self.items = []

    def enqueue(self, item):
        if self.capacity is not None and self.size() >= self.capacity:
            raise Exception("Queue is full")
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items.pop(0)

    def peak(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items[0]

    def rear(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def is_full(self):
        if self.capacity is None:
            return False
        return len(self.items) >= self.capacity

    def size(self):
        return len(self.items)

    def as_list(self):
        return list(self.items)


class PieceGenerator:
    def __init__(self, grid):
        self.grid = grid
        # Initialize bag and next_pieces as Queues.
        self.bag = Queue()  # No capacity limit needed for the bag.
        self.next_pieces = Queue(capacity=5)  # Queue for next pieces with capacity 5.
        self.queue_size = 5    # Show next 5 pieces
        self.generate_new_bag()
        self.fill_queue()      # Fill the initial queue

    def generate_new_bag(self):
        pieces = list('IOTSZJL')
        random.shuffle(pieces)

        ####################################
        # GROUP A SKILL : Queue Operations #
        ####################################

        self.bag = Queue()
        for piece in pieces:
            self.bag.enqueue(piece)

    def get_next_piece_from_bag(self):
        if self.bag.is_empty():
            self.generate_new_bag()
        
        ####################################
        # GROUP A SKILL : Queue Operations #
        ####################################

        shape = self.bag.dequeue()
        return Tetromino(shape, self.grid)

    def fill_queue(self):
        """Fill the queue up to queue_size pieces"""

        ####################################
        # GROUP A SKILL : Queue Operations #
        ####################################

        while self.next_pieces.size() < self.queue_size:
            self.next_pieces.enqueue(self.get_next_piece_from_bag())

    def get_next_piece(self):
        current_piece = self.next_pieces.dequeue()  # Remove the first piece from the queue
        self.fill_queue()  # Refill the queue to maintain the queue size
        return current_piece

    def preview_next_pieces(self):
        """Return list of next pieces"""

        ####################################
        # GROUP A SKILL : Queue Operations #
        ####################################
        
        return self.next_pieces.as_list()
