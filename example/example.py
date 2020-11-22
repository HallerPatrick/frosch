import sys
sys.path.append("..")

import numpy as np

from frosch.frosch import hook

from lib import fails

def display_np_array(np_array, config=None) -> str:
    if config == None:
        config = dict()

    result = ""
    if config.get('np_array.shape', True):
        result = f'{result} {np_array.shape}'

    if config.get('np_array.dtype', True):
        dtype = { np.dtype('float32'): 'f32',
                  np.dtype('float64'): 'f64',
                  np.dtype('int8'): 'i8',
                  np.dtype('int16'): 'i16',
                  np.dtype('int32'): 'i32',
                  np.dtype('int64'): 'i64',
                  np.dtype('uint8'): 'ui8',
                  np.dtype('uint16'): 'ui16',
                  np.dtype('uint32'): 'ui32',
                  np.dtype('uint64'): 'ui64',
                  np.dtype('bool'): 'ui64',
                  np.dtype('str'): 'str',
                  np.dtype('object'): 'obj',
                  }.get(np_array.dtype, 'unknown')

        result = f'{result}[{dtype}]'

    if config.get('np_array.finite', True):
        nan = np.isnan(np_array).sum()
        inf = np.isinf(np_array).sum()
        if nan>0:
            warning_marker = lambda x: f'!!{x}!!' # It would mark the content as warning, e.g. coloring to red
            nan = warning_marker(f'NaNs:{nan}')
        else:
            nan = f'NaNs:{nan}'

        result = f'{result} {nan} Infs:{inf}'

    if config.get('np_array.stat', True):
        if np_array.dtype not in (np.dtype('str'),np.dtype('object')):
            tmp = np_array.ravel()
            tmp = tmp[np.isfinite(tmp)]
            min_ = tmp.min()
            max_ = tmp.max()
            med_ = np.median(tmp)
            result = f'{result} min:{min_} max:{max_} median:{med_}'

    # I assume the array will be printed anyway
    # So i expect it in this form:
    # VARIABLE = {result} \n
    #            [[ .... ],
    #               .....]]

    return result

def hello():
    hook(theme="friendly", message="LOL", title="ITS DONE", dt_hooks = {
        np.array: display_np_array
    })

    y = "Some String"
    z = [1, 2, "hel"]
    index = 0
    i = "Other string"
    x = np.array([1, 2, 3])
    print(x)
    array = x + "3"



hello()
