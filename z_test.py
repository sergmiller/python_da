import numpy as np
import page_rank

N = 25
SIZE_MULT = 10**3

links, urls = page_rank.get_links('http://wikipedia.org/wiki/', N)
