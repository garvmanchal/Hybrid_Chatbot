import hashlib
import math


def embedding_text(text: str) ->list[float]:
    vec = [0.0] * 32 # means repeat that value 32 times, it creating a 32-dimensional vector
    for word in text.lower().split():
        bucket = int(hashlib.md5(word.encode()).hexdigest(),16) % 32

        vec[bucket] +=1.0

    norm = math.sqrt(sum(v*v for v in vec)) or  1.0  # norm refers to lenth or magnitude of the vec 
    return[v/ norm for v in vec]   # Take every value v in vec and divide it by norm.

# embedding_text() → converts text into a numerical vector.
# cosine_sim : compares two vectors to see how similar they are 

def cosine_sim(a:list[float] , b :list[float]) -> float:
    return sum(x * y for x,y in zip(a,b))



