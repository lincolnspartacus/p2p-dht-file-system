import pickle as pkl
import os

def circular_distance(start, end, M):
    distance = end - start
    if distance < 0:
        distance += 2**M
    
    return distance

def atomic_pkl_dump(python_obj, filename):
    tmpfile = filename + "2"
    with open(tmpfile, 'wb') as f:
        pkl.dump(python_obj, f)
        f.flush()
        os.fsync(f.fileno())
    
    os.rename(tmpfile, filename)

chunk_size = 65536
