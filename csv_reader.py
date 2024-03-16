import pandas as pd
import numpy as np

def read_contractor_sequence(filename = "conseq.xlsm - TASK.csv"):
    df = pd.read_csv(filename)
    df = df.iloc[1:]
    edges = []
    
    task_activity_map = {}
    
    for row in df.iterrows():
        task_activity_map[row[1]['task_code']] = row[1]['task_name']
        
        if row[1]["pred_details"] is np.nan:
            edges.append(("start", row[1]['task_name']))    
        
        else:
            edges.append((task_activity_map[row[1]["pred_details"][:3]], row[1]['task_name']))   
            
    
        
    return edges