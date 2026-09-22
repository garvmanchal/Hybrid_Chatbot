import hashlib
import math


def embedding_text(text: str) ->list[float]:
    vec = [0.0] * 32
    for word in text.lower().split():
        bucket = int(hashlib.md5(word.encode()).hexdigest(),16) % 32

        vec[bucket] +=1.0

    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return[v/ norm for v in vec]


def cosine_sim(a:list[float] , b :list[float]) -> float:
    return sum(x * y for x,y in zip(a,b))



