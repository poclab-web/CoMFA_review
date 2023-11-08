import pandas as pd
import numpy as np
from itertools import product
import os

out_dir_name="../penalty_param"
out_file_name="/penalty_param.csv"
if __name__ == '__main__':#cbsだいたい0.01あたりから,dip0.1あたりから
    # sr = {"λ1":np.arange(0.05,0.2,0.05)*10,
    #       "λ2":np.arange(0.05,0.2,0.05)*10}
    # sr = {"λ1": [0.01,0.05,0.1,0.5,1,5,10],
    #       "λ2": [0.01,0.05,0.1,0.5,1,5,10]}
    sr = {"λ1": [ 0.05,0.1, 0.5,1,5],
          "λ2": [ 0.05,0.1,0.5, 1,5],
          "λ3":[0.05,0.1,0.5,1.5]}
    # sr = {"λ1": [0.1, 0.5, 1, 5],
    #       "λ2": [ 0.1, 0.5, 1, 5]}
    dfp = pd.DataFrame([dict(zip(sr.keys(), l)) for l in product(*sr.values())]).astype(float)
    os.makedirs(out_dir_name,exist_ok=True)
    dfp.to_csv(out_dir_name+"/"+out_file_name)