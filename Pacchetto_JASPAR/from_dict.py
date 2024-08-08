import pandas as pd
from . import Objects

def from_dict(dic): #define a function to convert a properly written dictionary in a JASPAR_element
        data_frame = pd.json_normalize(dic["PFM"]) #convert the element (list of dictionarries) into a pd.DataFrame. NOTE: the function json_normalize works in a records oriented way (so each dictionary in the list is a row)
        data_frame.index = ["A","C","G","T"] #Hardcoded since the JASPAR documentation specifies the format structure
        JASPAR_obj = Objects.JASPAR_elem(dic["JASPAR_ID"],dic["TF_name"], data_frame)
        return JASPAR_obj #return the object