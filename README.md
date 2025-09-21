# SAXS analyse

Gaussian processing and transformer model for classification SAXS data 

for running

choose peak and phase kernels (algorithms of classification) for your data
and its paths to .csv files. 

after call an instance of manager class. 


# todo

- Replace deque.popleft() → use list + index to avoid function call overhead.
- Batch process samples → if stages can handle arrays, vectorize NumPy operations.
- Minimize Python object creation → reuse metadata, requests, and temporary objects.
- Use numba / JIT compilation → compile loops if Python overhead dominates.
- Parallelize independent stages → with ThreadPoolExecutor if process releases GIL.


# ?

- inplace ops?
- instance or class injections?
- lambda for state factory in injections?
- metaclass for logging
- pydantic for gluing metadata between stages