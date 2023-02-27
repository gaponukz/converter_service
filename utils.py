import math

def devide_list(array: list, number: int) -> list[list]:
    div_number = math.ceil(len(array) / number)
    result: list[list] = []
    start_index = 0

    for index in range(1, div_number+1):
        result.append(array[start_index:index*number])

        start_index = index * number
    
    return result