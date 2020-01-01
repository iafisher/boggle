#!/usr/bin/env python3
import bisect
import random
import readline
import shutil
import textwrap
import time
import unittest


DICTIONARY = "words.txt"
GAME_DURATION_IN_SECS = 3*60
BOARD_SIDE_LENGTH = 4


def main():
    dct = open_dictionary()
    board = make_board()
    print_board(board)
    print("Enter !p to print the board again.")
    print()
    start = now()
    end = time_add(start, GAME_DURATION_IN_SECS)
    your_words = set()
    while True:
        minutes, seconds = divmod(time_diff(end, now()), 60)
        minutes = int(minutes)
        seconds = int(seconds)

        try:
            response = input(f"({minutes}:{seconds:0>2}) > ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        else:
            response = response.strip().lower()

        if now() >= end:
            print("Time is up.")
            break

        if response == "!p":
            print_board(board)
        elif response:
            if response in your_words:
                print("You already said that.")
            else:
                if not check_board(board, response):
                    print("Not on the board.")
                    continue

                if not check_dictionary(dct, response):
                    print("Not in dictionary.")
                    continue

                your_words.add(response)

    all_possible_words = all_words(dct, board)
    best_possible_score = score(all_possible_words)
    your_score = score(your_words)
    perc = your_score / best_possible_score
    missed = sorted(all_possible_words - your_words)

    print()
    print(f"Your score:         {your_score}")
    print(f"Max possible score: {best_possible_score}")
    print(f"Efficiency:         {perc:.1%}")
    print()
    width = shutil.get_terminal_size()[0]
    print(textwrap.fill("MISSED: " + ", ".join(missed), width=width))


LETTERS = (
    (["a"] * 9) + (["b"] * 2)  + (["c"] * 2) + (["d"] * 4) + (["e"] * 12) +
    (["f"] * 2) + (["g"] * 3)  + (["h"] * 2) + (["i"] * 9) + (["j"] * 1) +
    (["k"] * 1) + (["l"] * 4)  + (["m"] * 2) + (["n"] * 6) + (["o"] * 8) +
    (["p"] * 2) + (["qu"] * 2) + (["r"] * 6) + (["s"] * 4) + (["t"] * 6) +
    (["u"] * 4) + (["v"] * 2)  + (["w"] * 2) + (["x"] * 1) + (["y"] * 2) +
    (["z"] * 1)
)
def make_board():
    return random.sample(LETTERS, BOARD_SIDE_LENGTH * BOARD_SIDE_LENGTH)


def print_board(board):
    print()
    for i in range(BOARD_SIDE_LENGTH):
        print("  ", end="")
        for j in range(BOARD_SIDE_LENGTH):
            letter = board[i*BOARD_SIDE_LENGTH+j].upper()
            if len(letter) == 2:
                print(letter + " ", end="")
            else:
                print(letter + "  ", end="")
        print()
    print()


def score(words):
    score = 0
    for word in words:
        if len(word) == 3 or len(word) == 4:
            score += 1
        elif len(word) == 5:
            score += 2
        elif len(word) == 6:
            score += 3
        elif len(word) == 7:
            score += 5
        elif len(word) >= 8:
            score += 11
    return score


def all_words(dct, board):
    words = set()
    for i in range(BOARD_SIDE_LENGTH * BOARD_SIDE_LENGTH):
        words |= set(all_words_search(dct, board, i, board[i], frozenset()))
    return words


def all_words_search(dct, board, index, so_far, already_used):
    dct_index = bisect.bisect_left(dct, so_far)
    if dct_index == len(dct):
        return

    if dct[dct_index] == so_far and len(so_far) >= 3:
        yield so_far

    # No word in the dictionay starts with this sequence, so we can prematurely
    # terminate.
    if not dct[dct_index].startswith(so_far):
        return

    for adjacent_index in adjacent(index):
        if adjacent_index in already_used:
            continue

        so_far2 = so_far + board[adjacent_index]
        already_used2 = already_used | {adjacent_index}
        yield from all_words_search(dct, board, adjacent_index, so_far2, already_used2)


def check_dictionary(dct, word):
    index = bisect.bisect_left(dct, word)
    return index < len(dct) and dct[index] == word


def check_board(board, word):
    if word.startswith("qu"):
        first, rest = word[:2], word[2:]
    else:
        first, rest = word[0], word[1:]

    index = find(board, first)
    while index != -1:
        if can_spell(board, rest, index, frozenset([index])):
            return True
        index = find(board, first, index+1)

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
