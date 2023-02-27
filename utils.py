import math

def devide_list(array: list, number: int) -> list[list]:
    if len(array) <= number:
        return [array]
    
    div_number = math.ceil(len(array) // number)
    result: list[list] = []
    start_index = 0

    for index in range(1, number+2):
        result.append(array[start_index:index*div_number])

        start_index = index * div_number
    
    return result
