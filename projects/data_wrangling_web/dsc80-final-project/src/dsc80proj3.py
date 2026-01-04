# project.py


import pandas as pd
import numpy as np
from pathlib import Path
import re
import requests
import time


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def get_book(url, pause=0.5):
    response = requests.get(url)
    text = response.text

    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"

    start_index = text.find(start_marker)
    end_index = text.find(end_marker)

    start_line_end = text.find("\n", start_index)
    book_text = text[start_line_end:end_index]
    book_text = book_text.replace('\r\n', '\n')
    time.sleep(pause)
    return book_text


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def tokenize(book_string):
    paragraphs = re.split(r'\n{2,}', book_string.strip())

    tokens = []
    for para in paragraphs:
        if not para.strip():
            continue

        tokens.append('\x02')

        tokens += re.findall(r"[A-Za-z0-9_]+|[^\w\s]", para)

        tokens.append('\x03')

    return tokens


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


class UniformLM:
    def __init__(self, tokens):
        self.mdl = self.train(tokens)

    def train(self, tokens):
        unique_tokens = pd.Series(tokens).unique()
        
        if len(unique_tokens) == 0:
            return pd.Series(dtype=float)
            
        prob = 1.0 / len(unique_tokens)
        return pd.Series(prob, index=unique_tokens)

    def probability(self, seq):
        prob = 1.0
        for token in seq:
            if token not in self.mdl.index:
                return 0.0 
            prob *= self.mdl[token]
        return prob

    def sample(self, M):
        sampled_tokens = np.random.choice(self.mdl.index, size=M, replace=True)
        return ' '.join(sampled_tokens)



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


class UnigramLM:
    def __init__(self, tokens):
        self.mdl = self.train(tokens)

    def train(self, tokens):
        return pd.Series(tokens).value_counts(normalize=True)

    def probability(self, seq):
        prob = 1.0
        for token in seq:
            if token not in self.mdl.index:
                return 0.0  
            prob *= self.mdl[token]
        return prob

    def sample(self, M):
        sampled_tokens = np.random.choice(
            self.mdl.index, 
            size=M, 
            replace=True, 
            p=self.mdl.values
        )
        return ' '.join(sampled_tokens)

# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


from collections import Counter, defaultdict

class NGramLM(object):

    def __init__(self, N, tokens):

        self.N = N

        ngrams = self.create_ngrams(tokens)

        self.ngrams = ngrams
        self.mdl = self.train(ngrams)

        if N < 2:
            raise Exception('N must be greater than 1')
        elif N == 2:
            self.prev_mdl = UnigramLM(tokens)
        else:
            self.prev_mdl = NGramLM(N-1, tokens)


    def create_ngrams(self, tokens):
        toks = list(tokens)
        n = self.N
        ngrams = []
        for i in range(len(toks) - n + 1):
            ngram = tuple(toks[i : i + n])
            ngrams.append(ngram)
        return ngrams


    def train(self, ngrams):
       
        ngram_counts = Counter(ngrams)
        n1gram_counts = Counter([ng[:-1] for ng in ngrams])

        rows = []
        temp_map = defaultdict(lambda: [[], []])  

        for ng, cnt in ngram_counts.items():
            n1g = ng[:-1]
            count_n1g = n1gram_counts[n1g]
            prob = cnt / count_n1g
            rows.append({"ngram": ng, "n1gram": n1g, "prob": prob})

            temp_map[n1g][0].append(ng[-1])
            temp_map[n1g][1].append(prob)

        df = pd.DataFrame(rows)

        probs_map = {}
        for n1g, (next_tokens, probs_list) in temp_map.items():
            arr = np.array(probs_list, dtype=float)
            s = arr.sum()
            if s <= 0:
                arr = np.ones_like(arr) / len(arr)
            else:
                arr = arr / s
            probs_map[n1g] = (next_tokens, arr)

        self._probs_map = probs_map

        return df


    def probability(self, words):
        
        prob = 1.0
        L = len(words)

        for i in range(L):
            context_size = min(self.N - 1, i)
            needed_order = context_size + 1   
            ngram = tuple(words[i - context_size : i + 1])

            model = self
            while hasattr(model, "N") and model.N > needed_order:
                model = model.prev_mdl
            if not hasattr(model, "N") or getattr(model, "N", 1) == 1:
                p = model.probability((ngram[-1],))
                if p == 0:
                    return 0.0
                prob *= p
                continue

            df = model.mdl
            row = df[df["ngram"] == ngram]
            if row.empty:
                return 0.0
            p = float(row["prob"].iloc[0])
            prob *= p

        return prob


    def sample(self, M):
    
        current = ['\x02']

        while len(current) < M + 1:
            context_size = min(self.N - 1, len(current) - 1)   
            if context_size <= 0:
                context = ()
            else:
                context = tuple(current[-context_size:])

            tried_order = context_size + 1
            next_token = None

            model = self
            while hasattr(model, "N") and model.N > tried_order:
                model = model.prev_mdl

            while tried_order >= 1:
                if tried_order == 1:
                    
                    uni_model = model
                    while hasattr(uni_model, "prev_mdl") and hasattr(uni_model, "N"):
                        uni_model = uni_model.prev_mdl
                    if hasattr(uni_model, "sample"):
                        try:
                           
                            uni_token = uni_model.sample(1)
                            if isinstance(uni_token, str):
                                toks = uni_token.split()
                                
                                if len(toks) >= 2:
                                    cand = toks[-2] if toks[-1] == '\x03' else toks[-1]
                                else:
                                    cand = toks[-1]
                                next_token = cand
                            else:
                                next_token = uni_token
                        except Exception:
                            try:
                                if hasattr(uni_model, "mdl") and isinstance(uni_model.mdl, pd.DataFrame):
                                 
                                    tokens = list(uni_model.mdl['ngram'].apply(lambda x: x[0]))
                                    probs = uni_model.mdl['prob'].values
                                    next_token = np.random.choice(tokens, p=probs)
                                else:
                                   
                                    next_token = '\x03'
                            except Exception:
                                next_token = '\x03'
                    else:
                        next_token = '\x03'

                  
                    if next_token is None:
                        next_token = '\x03'
                    current.append(next_token)
                    
                    if len(current) == M + 1:
                        break
                    break

                while hasattr(model, "N") and model.N > tried_order:
                    model = model.prev_mdl

                ctx = tuple(current[-(tried_order - 1):]) if (tried_order - 1) > 0 else ()

                pm = getattr(model, "_probs_map", None)
                if pm is not None and ctx in pm:
                    tokens_list, probs_arr = pm[ctx]
                    
                    next_token = np.random.choice(tokens_list, p=probs_arr)
                    current.append(next_token)
                    break

               
                tried_order -= 1
                if hasattr(model, "prev_mdl"):
                    model = model.prev_mdl

            if len(current) < 1 or (len(current) >= 1 and current[-1] not in (None,)):
                
                pass
            else:
                current.append('\x03')

            if current[-1] == '\x03':
                break

        return " ".join(current)
