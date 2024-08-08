import os
import json
import logomaker
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') #set the correct backend for matplotlib
import matplotlib.pyplot as plt

from sklearn.preprocessing import normalize

current_path = os.path.dirname(os.path.abspath(__file__)) #obtaining the script's directory path
target_path = os.path.join(current_path, '..', 'JASPAR_Images') #define a target path for images

#define a set of exception that will be useful in different occasions

class Dictionary_Exception(Exception):
    def __str__(self):
        return "ERROR! Wrong or incomplete keys were used when creating a dictionary"
    
class DataFrame_Exception(Exception):
    def __str__(self):
        return "ERROR! PFM MUST be a pd.DataFrame object"

class JASPAR_elem_Exception(Exception):
    def __str__(self):
        return "ERROR! Inserted object MUST be a JASPAR_elem object"

class Character_Exception(Exception):
    def __str__(self):
        return "ERROR! Make sure you have only inserted accepted characters! (A, C, G, T)"

class PFM_Exception(Exception):
    def __str__(self):
        return "ERROR! The length of the PFM field MUST be 4! One for each base! (A, C, G, T)"

class Length_Exception(Exception):
    def __str__(self):
        return "ERROR! Each base record MUST contain the same number of elements!"

#define the core of the package: JASPAR_elem, which how I thought of handling the data contiained in the JASPAR database

class JASPAR_elem:
    
    def __init__(self, JASP, TF_name, matrix): #define the constructor of the objects. When the object is created, 3 setters are called
        self.set_JASP(JASP)
        self.set_TF_name(TF_name)
        self.set_MATRIX(matrix)
   
    def find_consensus(self, mat): #define a function to find the consensus sequence of each object 
        consensus_index = mat.idxmax() #the index of the dataframe, corresponding to the highest value is taken as a reference
        self.consensus_sequence = "".join(consensus_index.astype(str)) #the indexes associated to the highest values in the matrix are converted to a string
    
    def get_LENGTH(self): #define a getter for the length of the motif
        return self.length
    
    def get_CONSENSUS(self): #define a getter for the consensus sequence of the motif
        return self.consensus_sequence
    
    def get_JASP(self): #define a getter for the JASPAR_ID of the motif
        return self.JASP
    
    def set_JASP(self, new_JASP): #define a setter for the JASPAR_ID of the motif
        self.JASP = str(new_JASP)
    
    def get_TF_name(self): #define a getter for the TF_name of the motif
        return self.TF_name
    
    def set_TF_name(self, new_TF_name): #define a setter for the TF_name of the motif
        self.TF_name = new_TF_name 
    
    def get_MATRIX(self): #define a getter for the PFM of the motif
        return self.matrix
    
    def set_MATRIX(self, new_matrix): #define a setter for the PFM of the motif
        try:
            if type(new_matrix) == pd.DataFrame: #check if the type is correct
                self.matrix = new_matrix
                self.matrix.columns = ["" for col in self.matrix.columns] #set the column names are empty spaces for better layout
                self.length = self.matrix.shape[1] #set the length of the motif based on the matrix
                self.find_consensus(self.matrix) #find the consensus sequence based on the matrix
                self.norm_mat = pd.DataFrame(normalize(self.matrix, axis = 0, norm = "l1")) #create the normalized PFM for the motif, which is the matrix of the frequencies of each base at each position
                self.norm_mat.index = self.matrix.index.values #set the indexes of the normalized PFM as the same of the regular PFM
                self.norm_mat.columns = ["" for col in self.norm_mat.columns] #set the column names are empty spaces for better layout
            else:
                raise DataFrame_Exception
        except DataFrame_Exception as e:
            return str(e)
    
    def get_NORM_MATRIX(self): #define a getter for the normalized PFM of the motif
        return self.norm_mat
    
    def to_dict(self): #define a method to convert the element to a dictionary, useful to easily convert the motif to a JSON string, since the dictionary is JSON serializable
        self.matrix.columns = range(1,self.matrix.shape[1]+1) #name the columns of the matrix in order to avoid ambiguity issues during the conversion 
        #create the dictionary representation of the object 
        #Please note that, since the set_MATRIX method also creates the consensus sequence and the length attribute, 
        #only these 3 fundamental attributes are necessary when converting the element to a dictionary or when creating an object from a dictionary
        JASPAR_dict = { "JASPAR_ID" : self.JASP, 
                        "TF_name" : self.TF_name,
                        "PFM" : self.matrix.to_json(orient = 'records')} #the pd.Dataframe is converted to a JSON string, oriented records-wise, so we will have a representation of a list of dictionaries, where each dictionary is one row 
        self.matrix.columns = ["" for col in self.matrix.columns] #reset the column names as empty spaces for better layout
        return JASPAR_dict
 
    def create_logo(self): #define a function that creates the logo representation of the motif, saving it in the IMAGES folder
        plt.figure() #create a new figure
        self.freq = self.norm_mat.T #transpose the frequency matrix
        self.freq.columns = self.matrix.index.values #set the column names as the name of the indexes
        self.freq.index = range(1,self.length + 1) #set the indexes of the transposed matrix
        self.freq.replace(0, 10**-10, inplace = True) #in order to avoid errors when using the logarithm, replace 0 values with a small number
        self.freq["IC"] = (2 - (-np.sum(self.freq * np.log2(self.freq), axis = 1))) #compute the Information Content as 2 - Shannnon's entropy
        for column in self.freq.iloc[:,0:4]:
            self.freq[column] = self.freq[column] * self.freq.iloc[:,-1] #update the value in the columns of the frequency matrix to the values that will be used for plotting, which is frequency value * Information Content
            
        self.freq = self.freq.iloc[:,:-1] #remove the Information Content column
        
        #create the logo of the motif
        
        logo = logomaker.Logo(self.freq,
                              width = 0.8,   
                              baseline_width=0,
                              font_name = "Consolas")
        
        plt.title(f'{self.JASP}', loc = 'center', fontsize = 12)
        logo.ax.set_ylabel("Bits", labelpad = 20)
        logo.ax.set_yticks([0, 0.5, 1, 1.5, 2])
        logo.ax.set_xticks(range(1,self.length + 1))
        logo.ax.xaxis.set_ticks_position('none')
        logo.ax.yaxis.set_ticks_position('none')
        logo.style_spines(visible=False)
        logo.ax.tick_params(axis='both', which='major', labelsize=6)
        plt.savefig(f"{target_path}/{self.JASP}.png", dpi = 350) #save the created logo in the IMAGES folder inside the main folder

    def __str__(self): #define the __str__ method for a pretty printed output
        out = f'\nJASPAR_ID: {self.JASP}\nCorresponding TF name: {self.TF_name}\nMotif Length: {self.length}\nConsensus Sequence: {self.consensus_sequence}\n{self.matrix}\n\n'
        return out