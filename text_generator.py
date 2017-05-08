#!/usr/bin/env python3
import argparse
import unittest
import random
from copy import copy
from collections import deque

NOT_ALPHA_DIGIT_INDEX = 2
FREQUENCIES_PRINT_FORMAT = '  {}: {:.2f}'


def _get_token_lines(text):
    tokenizers = [
        (lambda s: s.isalpha()),
        (lambda s: s.isdigit()),
        (lambda s: not (s.isalpha() or s.isdigit()))
    ]

    token_lines = []

    for line in text:
        cur_token = None
        tokens = []
        for symb in line:
            if cur_token is None or\
                tokenizers[NOT_ALPHA_DIGIT_INDEX](symb) or\
                    not cur_token(symb):
                cur_token = [f for f in tokenizers if f(symb)][0]
                tokens.append('')
            tokens[-1] += symb
        token_lines.append(tokens)

    return token_lines


def tokenize(arg_list):
    text = input_text()
    token_lines = _get_token_lines(text)
    for tokens in token_lines:
        for token in tokens:
            print(token)


def _build_frequencies(depth, token_lines):
    go = dict()
    turn_sums = dict()

    for tokens in token_lines:
        history = deque()
        for token in tokens:
            if token.isalpha():
                removed = deque()
                update_lens = len(history) + 1
                for i in range(update_lens):
                    cur_frozen_history = tuple(history)
                    cur_turn = (cur_frozen_history, token)

                    if len(history):
                        removed.append(history.popleft())

                    if cur_turn not in go:
                        go[cur_turn] = 0

                    if cur_frozen_history not in turn_sums:
                        turn_sums[cur_frozen_history] = 0

                    go[cur_turn] += 1
                    turn_sums[cur_frozen_history] += 1
                history = removed
                history.append(token)
                if len(history) > depth:
                    history.popleft()

    for key in go:
        go[key] = (go[key], turn_sums[key[0]])  # frequency as rational
    return go


def _get_frequencies(depth, text):
    token_lines = _get_token_lines(text)
    frequencies = _build_frequencies(depth, token_lines)
    return frequencies


def probabilities(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth', type=int)
    args = parser.parse_args(arg_list)
    text = input_text()
    frequencies = _get_frequencies(args.depth, text)
    turns = dict()
    for key in frequencies:
        if key[0] not in turns:
            turns[key[0]] = []
        turns[key[0]].append(key[1])

    turns = {key: sorted(turns[key]) for key in turns}

    for from_token in sorted([key for key in turns]):
        print(' '.join(from_token))
        for to_token in turns[from_token]:
            cur_freq_data = frequencies[(from_token, to_token)]
            print(FREQUENCIES_PRINT_FORMAT.format(
                to_token,
                cur_freq_data[0] / cur_freq_data[1]
                ))


def _get_next_with_random(history, frequencies):
    history = tuple(history)
    suitable_moves = [key[1] for key in frequencies if key[0] == history]
    if len(suitable_moves) == 0:
        return None
    generator_bound = frequencies[(history, suitable_moves[0])][1]
    rnd_var = random.randint(1, generator_bound)
    result = 0
    while True:
        cur_move_number = frequencies[(history, suitable_moves[result])][0]
        if rnd_var > cur_move_number:
            rnd_var -= cur_move_number
            result += 1
        else:
            break
    return suitable_moves[result]


def _generate_random_text_from(text, depth, size):
    frequencies = _get_frequencies(depth, text)
    generated_text = []
    history = deque()
    for t in range(size):
        next_token = _get_next_with_random(history, frequencies)
        if next_token is None:
            next_token = _get_next_with_random([], frequencies)
            history = deque()
        history.append(next_token)
        if len(history) > depth:
            history.popleft()
        generated_text.append(next_token)
    return generated_text


def generate(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth', type=int)
    parser.add_argument('--size', type=int)
    args = parser.parse_args(arg_list)
    text = input_text()
    text_tokens = _generate_random_text_from(text, args.depth, args.size)
    generated_text = []
    for token in text_tokens:
        if token[0].isupper() and len(generated_text) > 0:
            generated_text[-1] += '.'
        generated_text.append(token)
    if len(generated_text):
        generated_text[-1] += '.'
    first_word = generated_text[0]
    generated_text[0] = first_word[0].upper() + first_word[1:]
    print(' '.join(generated_text))


class TestTextGenerator(unittest.TestCase):
    def test_get_token_lines(self):
        self.assertEqual(_get_token_lines(
            text=['Hello, world!', 'First test 2line']),
            [
                ['Hello', ',', ' ', 'world', '!'],
                ['First', ' ', 'test', ' ', '2', 'line']
            ])

    def test_build_frequencies(self):
        self.assertEqual(_build_frequencies(
            depth=2,
            token_lines=[
                ['First', ' ', 'test', ' ', 'sentence'],
                ['Second', ' ', 'test', ' ', 'line']
                ]),
                {
                    ((), 'First'): (1, 6),
                    ((), 'test'): (2, 6),
                    ((), 'sentence'): (1, 6),
                    ((), 'Second'): (1, 6),
                    ((), 'line'): (1, 6),
                    (('First', ), 'test'): (1, 1),
                    (('test', ), 'sentence'): (1, 2),
                    (('test', ), 'line'): (1, 2),
                    (('Second', ), 'test'): (1, 1),
                    (('First', 'test', ), 'sentence'): (1, 1),
                    (('Second', 'test', ), 'line'): (1, 1)
                }
        )

    def test_get_next_with_random(self):
        self.assertTrue(
            _get_next_with_random(
                history=('test', ),
                frequencies={
                    ((), 'First'): (1, 6),
                    ((), 'test'): (2, 6),
                    ((), 'sentence'): (1, 6),
                    ((), 'Second'): (1, 6),
                    ((), 'line'): (1, 6),
                    (('First', ), 'test'): (1, 1),
                    (('test', ), 'sentence'): (1, 2),
                    (('test', ), 'line'): (1, 2),
                    (('Second', ), 'test'): (1, 1),
                    (('First', 'test', ), 'sentence'): (1, 1),
                    (('Second', 'test', ), 'line'): (1, 1)
                }
            ) in {'sentence', 'line'})

    def test_generate_random_text_from(self):
        text = [
            ['First test sentence'],
            ['Second test line']
        ]
        SIZE = 10
        DEPTH = 2
        random_text_tokens = _generate_random_text_from(
            text,
            depth=DEPTH,
            size=SIZE)
        frequencies = _build_frequencies(
            depth=DEPTH,
            token_lines=_get_token_lines(text))
        keys_tokens_from = [key[0] for key in frequencies]
        history = deque()
        self.assertEqual(len(random_text_tokens), SIZE)
        for i in range(SIZE - 1):
            cur_token = random_text_tokens[i]
            cur_turn = (tuple(history), cur_token)
            self.assertTrue(
                cur_turn in frequencies or
                history not in keys_tokens_from)
            history.append(cur_token)
            if len(history) > DEPTH:
                history.popleft()


def test(dummy_arg):
    unittest.main()


def input_text():
    text = []
    while True:
        try:
            text.append(input())
        except:
            break
    return text


def main():
    arg_list = input().split()
    options = {
        'tokenize': tokenize,
        'probabilities': probabilities,
        'generate': generate,
        'test': test
    }

    try:
        mode = options[arg_list[0]]
    except KeyError as ke:
        print('Nonexistent mode: ' + str(ke))

    mode(arg_list[1:])


if __name__ == "__main__":
    main()
