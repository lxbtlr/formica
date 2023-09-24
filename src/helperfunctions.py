import numpy as np
import time
import multiprocessing

DIRECTIONS= np.array([[315, 0, 45],[270, -1, 90],[225, 180,135]])


def round6(value):
    if value == 0:
        return 0.0
    else:
        return round(value, 6 - int(np.floor(np.log10(abs(value)))))

execution_times = {}
def timing(identifier):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            if identifier in execution_times:
                execution_times[identifier].append(execution_time)
            else:
                execution_times[identifier] = [execution_time]
            return result
        return wrapper
    return decorator

@timing("hf stat")
def calculate_statistics(input_dict):
    result_dict = {}
    for key, values in input_dict.items():
        if values:
            statistics_dict = {}
            values_array = np.array(values)
            
            statistics_dict["mean"]     = round6(np.mean(values_array))
            statistics_dict["median"]   = round6(np.median(values_array))
            statistics_dict["std_dev"]  = round6(np.std(values_array))
            statistics_dict["variance"] = round6(np.var(values_array))
            statistics_dict["min"]      = round6(np.min(values_array))
            statistics_dict["max"]      = round6(np.max(values_array))
            statistics_dict["count"]    = round6(len(values_array)   )
            statistics_dict["total_t"]  = round6(np.sum(values_array))
            result_dict[key] = statistics_dict
    return result_dict

@timing("hf rot45")
def rot45(matrix, direction="left"):
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Input matrix must be square (n x n)")
    n = matrix.shape[0]
    shifted_matrix = np.copy(matrix)
    if direction == "right":
        # Shift the top row to the right
        shifted_matrix[0, 1:] = matrix[0, :-1]
        # Shift the right column down
        shifted_matrix[1:, -1] = matrix[:-1, -1]
        # Shift the bottom row to the left
        shifted_matrix[-1, :-1] = matrix[-1, 1:]
        # Shift the left column up
        shifted_matrix[:-1, 0] = matrix[1:, 0]
    elif direction == "left":
        # Shift the top row to the left
        shifted_matrix[0, :-1] = matrix[0, 1:]
        # Shift the left column down
        shifted_matrix[1:, 0] = matrix[:-1, 0]
        # Shift the bottom row to the right
        shifted_matrix[-1, 1:] = matrix[-1, :-1]
        # Shift the right column up
        shifted_matrix[:-1, -1] = matrix[1:, -1]
    else:
        raise ValueError("Direction must be 'left' or 'right'")

    return shifted_matrix

@timing("hf flip")
def flip(p_true:float)->bool:
    if p_true > 1 or p_true < 0:
        raise ValueError(f"probability true must be in range [0,1]\np={p_true}")
    return np.random.random()<p_true


@timing("hf roll8")
def roll8(nmatrix, direction)->int:
    ''' 
    0 , 1 , 2
    3 ,>A<, 5
    6 , 7 , 8 
    '''
    flat = nmatrix.ravel()
    flat = np.nan_to_num(flat)
    #if flat[np.argpartition(flat,-2)[-2:]].sum() > .9 and flat.sum() != 0:
    #    #branches = np.count_nonzero(flat==np.max(flat))
    #    #if branches>2:
    #    #FIXME: THIS NEEDS TO BE CHANGED

    #    x,y  = deg2position(direction)
    #    outcome:int = int(x + y*3)
    #else:
    #    outcome:int = int(np.random.choice(range(0,9),1,p=flat))
    outcome:int = int(np.random.choice(range(0,9),1,p=flat))
    return outcome

@timing("hf sat2fid")
def saturation_to_fidelity( csat:int, max_sat, min_fid, max_fid=100,   )->float:
    # NOTE: this method maps the saturation value to fidelity
    
    # Calculate the percentage of input value within the input range
    input_percentage = csat / max_sat
    
    # Map the input percentage to the output range
    mapped_value = min_fid + (input_percentage * (max_fid - min_fid))
    if mapped_value > max_fid: mapped_value = max_fid
    return mapped_value

@timing("hf split")
def split_list(long_list:list, chunk_size:int)->list[list]:
    if not (len(long_list) >6):
        return [long_list]
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]

def process_section(board_dimensions:int,pc,section_agents:list)->tuple[list,list[int],list[int], int]:
    _ytmp = []
    _xtmp = []
    lost  = 0
    for ant in section_agents:
        
        _x,_y = ant.get_position()
        if _x < 1 or _x>board_dimensions-2 or _y <1 or _y > board_dimensions-2:
            ant.reset()
            _x,_y = ant.get_position()
        _xtmp.append(_x) 
        _ytmp.append(_y)
        ant.update(pc)
        lost += ant.is_lost()

    return (section_agents, _xtmp, _ytmp, lost)

#def multi(boardShape, list_chunks, pheromeone_concentration, processes=10):
#    #list_chunks = list(split_list(all_agents,processes))
#    with multiprocessing.Pool(processes=processes) as pool:
#    # Perform computations on each chunk in parallel
#        r = pool.map(process_section, boardShape, pheromeone_concentration, list_chunks)
#        
#        # Flatten the results list
#        results:list[Agent]       = [f for t in r for f in t[0]]
#        xtmp:list[int]            = [f for t in r for f in t[1]]
#        ytmp:list[int]            = [f for t in r for f in t[2]]
#        lost:int                  = sum([t[3] for t in r])
#        
#    # Update the original list with the processed results
#    
#    nboard[xtmp,ytmp] = 1
#    all_agents = results
#    pheromone_concentration = updatePheromone(pheromone_concentration, xtmp, ytmp)

if __name__ == "__main__":
    pass
