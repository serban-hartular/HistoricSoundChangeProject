
import dataclasses

def simple_string_distance(s : str, t : str) -> int:
    m = len(s)
    n = len(t)
    v0 = list(range(n+1))
    v1 = [0]*(n+1)
    for i in range(m):
        v1[0] = i + 1
        for j in range(n):
            # // calculating costs for A[i + 1][j + 1]
            deletionCost = v0[j + 1] + 1
            insertionCost = v1[j] + 1
            substitutionCost = v0[j] if s[i] == t[j] else v0[j]+1
            v1[j + 1] = min(deletionCost, insertionCost, substitutionCost)
        v0, v1 = v1, v0 # swap
    return v0[n]