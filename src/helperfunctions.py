import matplotlib.pyplot as mpl
import numpy as np
import csv 
import time
import multiprocessing

DIRECTIONS= np.array([[315, 0, 45],
                      [270, -1, 90],
                      [225, 180,135]])

displacement = np.array([[(-1,1),(0,1),(1,1)],
                         [(-1,0),(0,0),(1,0)],
                         [(-1,-1),(0,-1),(1,-1)]])


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

@timing("hf d2pos")
def deg2position(degrees):
    if degrees == 360: degrees = 0
    ind = np.where(DIRECTIONS == degrees)
    x,y = ind
    print(x,y)
    dx, dy = displacement[x[0]][y[0]]
    return dx, dy

@timing("hf r6")
def round6(value):
    if value == 0:
        return 0.0
    else:
        return round(value, 6 - int(np.floor(np.log10(abs(value)))))
@timing("hf stat")
def calculate_statistics(input_dict):
    result_dict = {}
    inny = input_dict.copy()
    for key, values in inny.items():
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

@timing("hf writestats")
def write_stats(results):
    with open('results.csv', mode='w', newline='') as csv_file:
        fieldnames = ['function', 'Mean', 'Median', 'Standard Deviation', 'Variance', 'Min', 'Max', 'Count', 'Total Time']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for list_name, statistics in results.items():
            writer.writerow({
                'function': list_name,
                'Mean': statistics['mean'],
                'Median': statistics['median'],
                'Standard Deviation': statistics['std_dev'],
                'Variance': statistics['variance'],
                'Min': statistics['min'],
                'Max': statistics['max'],
                'Count': statistics['count'],
                'Total Time':statistics['total_t']
            })

@timing("hf boardnorm")
def boardnorm(data):
    total = np.zeros((len(data[0]),len(data[0])))
    for d in data:
        total += d
    norm = np.linalg.norm(total,1)
    ntotal = total / norm
    return ntotal


@timing("hf savefig")
def save_figure(data, **kwargs):
    mpl.imshow(data, cmap='gray_r', vmin=0, vmax=kwargs.get('max',1))
    mpl.savefig(f"{kwargs.get('dir','img')}/{kwargs.get('name','heatmap')}.png", bbox_inches='tight')  

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


if __name__ == "__main__":
    pass
