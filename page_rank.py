import numpy as np
import networkx
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup


def create_markov_chain_turns(links, N, damping_factor=0.1):
    '''
        links - directed graph of links
        N - number of vertices
        damping_factor -- probability of turn without link
    '''

    prob_matrix = np.ones([N, N])*damping_factor/N

    L = np.zeros(N, dtype=int)  # number of links from

    for l in links:
        L[l[0]] += 1

    for l in links:
        prob_matrix[l[0]][l[1]] += (1-damping_factor)/L[l[0]]

    for i in range(N):
        if L[i] == 0:  # case with isolated vertex
            prob_matrix[i] = np.ones(N)/N

    return np.matrix(prob_matrix)


def page_rank(links, start_distribution, damping_factor=0.15,
              tolerance=10 ** (-7)):
    # estimate page_rank with power of prob_matrix
    prob_matrix = create_markov_chain_turns(
        links,
        len(start_distribution[0]),
        damping_factor=damping_factor)

    prev_distr = start_distribution
    cur_distr = start_distribution * prob_matrix

    while np.max(np.abs(prev_distr - cur_distr)) > tolerance:
        prev_distr = cur_distr
        cur_distr = cur_distr * prob_matrix

    distribution = cur_distr

    # if return_trace:
    #     return np.array(distribution).ravel(), np.array(trace)
    # else:
    return np.array(distribution).ravel()


def load_links(url, sleep_time=1, attempts=5, timeout=20):
    # load page from url

    sleep(sleep_time)  # just to avoid ban
    parsed_url = urlparse(url)
    links = []
    #  try to load
    for i in range(attempts):
        try:
            soup = BeautifulSoup(urlopen(url, timeout=timeout), 'lxml')
            break

        except Exception as e:
            print(e)
            if i == attempts - 1:
                raise e

    for tag_a in soup('a'):
        if 'href' in tag_a.attrs:
            link = list(urlparse(tag_a['href']))

            # convert local links to global
            if link[0] == '':
                link[0] = parsed_url.scheme

            if link[1] == '':
                link[1] = parsed_url.netloc

            links.append(urlunparse(link))

    return links


def get_site(url):
    return urlparse(url).netloc


def build_links(url, N, sleep_time):
    urls = []
    urls.append(url)
    urls_index = dict()
    links = []
    site = get_site(url)
    for i in range(N):
        try:
            links_from_url = load_links(urls[i], sleep_time)
            # filter outer links
            links_from_url = list(filter(lambda x: get_site(x) == site,
                                         links_from_url))

            # add new links to web-graph
            for j in range(len(links_from_url)):
                # link to old url
                if links_from_url[j] in urls_index:
                    links.append((i, urls_index[links_from_url[j]]))

                # link to new url
                else:
                    links.append((i, len(urls)))
                    urls_index[links_from_url[j]] = len(urls)
                    urls.append(links_from_url[j])

        except:
            pass

    return links, urls


def get_links(url, N, sleep_time=0.1):
    links, urls = build_links(url, N, sleep_time)
    return list(set(filter(lambda x: x[0] < N and x[1] < N, links))), urls[:N]


def get_graph(links, urls):
    N = len(urls)
    start_distribution = np.ones((1, N)) / N
    pr_distribution = page_rank(links, start_distribution)

    G = networkx.DiGraph()
    G.add_nodes_from(np.arange(N))
    G.add_edges_from(links)
    return G, pr_distribution
