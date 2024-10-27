def insert_ordered(item,array):
    
    if len(array) == 1: # base case
    
        if array[0].ID > item.ID:
            return [item] + array
    
        return array + [item]
    
    pos = len(array) // 2
    if array[pos].ID > item.ID:
        return insert_ordered(item,array[:pos]) + array[pos:]
    
    return array[:pos] + insert_ordered(item,array[pos:])
