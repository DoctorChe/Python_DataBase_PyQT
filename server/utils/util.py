from array import array
from itertools import islice


def get_chunk(text, size):
    text_iter = (char for char in text)
    chunk = array('B', islice(text_iter, size)).tobytes()
    text_residue = array('B', text_iter).tobytes()
    return chunk, text_residue
