from . import Objects
import pandas as pd

def get_single_score(obj, seq): #define a function to obtain the similarity score for one motif
    try:
        if type(obj) == Objects.JASPAR_elem: #check for the object type
            score = 1 #initialize the score as 1
            for i in range(obj.get_LENGTH()):
                base_score = obj.get_NORM_MATRIX().loc[seq[i]].iloc[i] #obtain the normalized matrix and the frequency for that base in that specific position
                score *= base_score #multiply it 
            return score
        else:
            raise Objects.JASPAR_elem_Exception
    except Objects.JASPAR_elem_Exception as e:
        return str(e)

def get_sequence_scores(seq, DB): #define a function to apply the previous function in the database
    scores_DB = [[str(elem.get_JASP()), elem.get_CONSENSUS(), str(get_single_score(elem, seq))] for elem in DB if len(elem.get_CONSENSUS()) == len(seq)] #obtain the ID, the consensus sequence and the similarity score for each of the elements in the database if the motif length is the same as the length of the provided sequence 
    scores_DB = sorted(scores_DB, key = lambda x: float(x[2]), reverse = True) #sort the list in descending order, so from the best scoring to the worst scoring
    if len(scores_DB) == 0: #if we have no sequences of such length
        return "There is no stored motif of such length!"
    else:
        scores_DB = ["\t".join(lis) for lis in scores_DB]
        return "\n".join(scores_DB)