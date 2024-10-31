import pandas as pd
import requests
import sys
from . import Objects #import the Objects module of my package

def DB_setup(how):
    #define a function that gets the whole database from the JASPAR website and preprocesses it, outputting the list containing all the database elements, in the form of self defined objects
    try:
        if how == "-r":
            URL = "https://jaspar.elixir.no/download/data/2024/CORE/JASPAR2024_CORE_redundant_pfms_jaspar.txt"
        elif how == "-nr":
            URL = "https://jaspar.elixir.no/download/data/2024/CORE/JASPAR2024_CORE_non-redundant_pfms_jaspar.txt"
        else:
            raise ValueError
    except ValueError as e:
        print("ERROR! Make sure to have correctly set the option! (either -r or -nr)")
        sys.exit(1)

    
    DB_raw = requests.get(URL).text.split(">")[1:] #I split each element using the > symbol
    DB_clean = []
    for motif in DB_raw:
        JASPAR_ID, TF_name = motif[:motif.index("\n")].split("\t") #the two elements are elements separated by a \t taken before the \n, since after the \n there's the PFM
        raw_matrix = motif[motif.index("\n")+1:].split("\n")[:-1] #I extract the PFM
        PFM = []
        base_order = []
        for row in raw_matrix:
            row = row.replace("[","") #remove the parenthesis
            row = row.replace("]","")
            row = row.split(" ")
            row = [chr for chr in row if chr.isalnum()] #retain only the alphanumeric elements
            base = row[0]
            val = list(map(int, row[1:])) #cast all the numeric values as integers
            PFM.append(val)
            base_order.append(base) #it could have been hardcoded since the order of the bases refers to the JASPAR format, but decided not to do that in earlier stages of development 
        PFM = pd.DataFrame(PFM, index = base_order) #create a dataframe using the numeric values in the list and the base order as index
        entry = Objects.JASPAR_elem(JASPAR_ID, TF_name, PFM) #create the object using the elements I defined
        DB_clean.append(entry) #append the element in the list   
    return DB_clean