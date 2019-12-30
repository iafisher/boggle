#!/usr/bin/env python3
import bisect
import random
import time
import unittest


DICTIONARY = "words.txt"
GAME_DURATION_IN_SECS = 3*60
BOARD_SIDE_LENGTH = 4


def main():
    words = open_dictionary()
    board = make_board()
    print_board(board)
    start = now()
    end = time_add(start, GAME_DURATION_IN_SECS)
    guesses = set()
    while True:
        minutes, seconds = divmod(time_diff(end, now()), 60)
        minutes = int(minutes)
        seconds = int(seconds)

        try:
            response = input(f"({minutes}:{seconds:0>2}) > ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if now() >= end:
            print("Time is up.")
            break

        if response == "!p":
            print_board(board)
        elif response:
            if response in guesses:
                print("You already said that.")
            else:
                if not check_board(board, response):
                    print("Not on the board.")
                    continue

                if not check_dictionary(words, response):
                    print("Not in dictionary.")
                    continue

                guesses.add(response)


# TODO: 'Q' and 'U' should be grouped together.
LETTERS = (
    ("A" * 9) + ("B" * 2) + ("C" * 2) + ("D" * 4) + ("E" * 12) +
    ("F" * 2) + ("G" * 3) + ("H" * 2) + ("I" * 9) + ("J" * 1) +
    ("K" * 1) + ("L" * 4) + ("M" * 2) + ("N" * 6) + ("O" * 8) +
    ("P" * 2) + ("Q" * 1) + ("R" * 6) + ("S" * 4) + ("T" * 6) +
    ("U" * 4) + ("V" * 2) + ("W" * 2) + ("X" * 1) + ("Y" * 2) +
    ("Z" * 1)
)
def make_board():
    return random.sample(LETTERS, BOARD_SIDE_LENGTH * BOARD_SIDE_LENGTH)


def print_board(board):
    print()
    for i in range(BOARD_SIDE_LENGTH):
        for j in range(BOARD_SIDE_LENGTH):
            print(" " + board[i*BOARD_SIDE_LENGTH+j], end="")
        print()
    print()


def check_dictionary(words, word):
    word = word.lower()
    index = bisect.bisect_left(words, word)
    return index < len(words) and words[index] == word


def check_board(board, word):
    word = word.upper()
    index = find(board, word[0])
    while index != -1:
        if can_spell(board, word[1:], index, frozenset([index])):
            return True
        index = find(board, word[0], index+1)

    return False


def can_spell(board, word, last_index, already_used):
    if not word:
        return True

    for index in adjacent(last_index):
        if index in already_used:
            continue

        if board[index] == word[0]:
            result = can_spell(board, word[1:], index, already_used | {index})
            if result:
                return True

    return False


def adjacent(index):
    if not top_edge(index):
        if not left_edge(index):
            yield above(left(index))

        yield above(index)

        if not right_edge(index):
            yield above(right(index))

    if not left_edge(index):
        yield left(index)

    if not right_edge(index):
        yield right(index)

    if not bottom_edge(index):
        if not left_edge(index):
            yield below(left(index))

        yield below(index)

        if not right_edge(index):
            yield below(right(index))


def top_edge(index): return index < BOARD_SIDE_LENGTH
def bottom_edge(index): return index >= (BOARD_SIDE_LENGTH * (BOARD_SIDE_LENGTH - 1))
def left_edge(index): return index % BOARD_SIDE_LENGTH == 0
def right_edge(index): return index % BOARD_SIDE_LENGTH == BOARD_SIDE_LENGTH - 1

def above(index): return index - BOARD_SIDE_LENGTH
def below(index): return index + BOARD_SIDE_LENGTH
def left(index): return index - 1
def right(index): return index + 1


def find(lst, item, start=0):
    for i, x in enumerate(lst):
        if x == item and i >= start:
            return i
    return -1


def open_dictionary():
    with open(DICTIONARY, "r", encoding="utf-8") as f:
        return f.read().split("\n")


def now():
    return time.monotonic()


def time_diff(t1, t2):
    return t1 - t2


def time_add(t, secs):
    return t + secs


class BoggleTest(unittest.TestCase):
    """Run with `python3 -m unittest boggle.py`."""

    def test_adjacent(self):
        #  0   1   2   3
        #  4   5   6   7
        #  8   9  10  11
        # 12  13  14  15
        self.assertEqual(set(adjacent(0)), {1, 4, 5})
        self.assertEqual(set(adjacent(1)), {0, 2, 4, 5, 6})
        self.assertEqual(set(adjacent(4)), {0, 1, 5, 8, 9})
        self.assertEqual(set(adjacent(9)), {4, 5, 6, 8, 10, 12, 13, 14})
        self.assertEqual(set(adjacent(12)), {8, 9, 13})
        self.assertEqual(set(adjacent(15)), {10, 11, 14})

    def test_check_board(self):
        # E Z O A
        # L T A R
        # N E L K
        # T S I B
        board = list("EZOALTARNELKTSIB")
        self.assertTrue(check_board(board, "A"))
        self.assertTrue(check_board(board, "TAR"))
        self.assertTrue(check_board(board, "SENT"))
        self.assertTrue(check_board(board, "LISTEN"))
        self.assertTrue(check_board(board, "RATES"))
        self.assertFalse(check_board(board, "TORE"))
        self.assertFalse(check_board(board, "QUEST"))
        # Cannot use the same 'T' twice.
        self.assertFalse(check_board(board, "TAT"))

    def test_check_dictionary(self):
        words = open_dictionary()
        self.assertTrue(check_dictionary(words, "mat"))
        self.assertTrue(check_dictionary(words, "MAT"))
        self.assertFalse(check_dictionary(words, "jkldfalkb"))

    def test_check_board_regressions(self):
        # U N E N
        # E E Q S
        # R Y N H
        # O P K R
        board = list("UNENEEQSRYNHOPKR")
        self.assertTrue(check_board(board, "pore"))


if __name__ == "__main__":
    main()
