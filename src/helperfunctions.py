import numpy as np



DIRECTIONS= np.array([[315, 0, 45],[270, -1, 90],[225, 180,135]])
def direction(falt_coord)->tuple[int,int]:
    ''' 
    ...
    '''
    return (1,1)

def deg2position(degrees):
    ind = np.where(DIRECTIONS == degrees)
    x,y = ind
    return x[0], y[0]

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

def flip(p_true:float)->bool:
    if p_true > 1 or p_true < 0:
        raise ValueError(f"probability true must be in range [0,1]\np={p_true}")
    return np.random.random()<p_true


def roll8(nmatrix, direction)->int:
    ''' 
    0 , 1 , 2
    3 ,>A<, 5
    6 , 7 , 8 
    '''
    flat = nmatrix.ravel()
    flat = np.nan_to_num(flat)
    if flat[np.argpartition(flat,-2)[-2:]].sum() > .9 and flat.sum() != 0:
        #branches = np.count_nonzero(flat==np.max(flat))
        #if branches>2:
        x,y  = deg2position(direction)
        outcome:int = int(x + y*3)
    else:
        outcome:int = int(np.random.choice(range(0,9),1,p=flat))
    return outcome

def saturation_to_fidelity( csat:int, max_sat, min_fid, max_fid=100,   )->float:
    # NOTE: this method maps the saturation value to fidelity
    
    # Calculate the percentage of input value within the input range
    input_percentage = csat / max_sat
    
    # Map the input percentage to the output range
    mapped_value = min_fid + (input_percentage * (max_fid - min_fid))
    if mapped_value > max_fid: mapped_value = max_fid
    return mapped_value


def split_list(long_list:list, chunk_size:int)->list[list]:
    if not (len(long_list) >6):
        return [long_list]
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]

def process_section(board_dimensions:tuple[int,int],pc,section_agents:list)->tuple[list,list[int],list[int], int]:
    _ytmp = []
    _xtmp = []
    lost  = 0
    for ant in section_agents:
        
        _x,_y = ant.get_position()
        if _x < 1 or _x>board_dimensions[0]-2 or _y <1 or _y > board_dimensions[1]-2:
            ant.reset()
            _x,_y = ant.get_position()
        _xtmp.append(_x) 
        _ytmp.append(_y)
        ant.update(pc)
        lost += ant.is_lost()

    return (section_agents, _xtmp, _ytmp, lost)

if __name__ == "__main__":
    pass
