def circular_distance(start, end, M):
    distance = end - start
    if distance < 0:
        distance += 2**M
    
    return distance