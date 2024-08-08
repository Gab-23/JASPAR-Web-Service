import sys
import os
import warnings
import unittest

#set the correct path for importing the package

current_path = os.path.dirname(os.path.realpath(__file__))
target_path = os.path.join(current_path, '..')
sys.path.insert(0, target_path)

from Pacchetto_JASPAR import DB_setup, Objects, from_dict #import the package

database = DB_setup.DB_setup() #create the database using the dedicated function

#define a unittest.TestCase class to test several aspects of the database

class Test_DB_work(unittest.TestCase):
        
    def setUp(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning) #Deprecation Warnings are not ignored by default when working in a UnitTest framework, since I want a clean output, I decided to ignore them
        
    def test_completeness_db(self): #define a test for assessing the completeness of the database. 
                                    #Since the creation of the database relies on a request from the official site of JASPAR, any Internet Connection problem nay provoke incompleteness in the database
        set_up_length = len(database)
        self.assertEqual(set_up_length, 2346, "DB_setup failed!") #check for the completeness of the database. Here the number is hardcoded since it's the expected number of motifs in the database

    def test_right_type(self): #define a test to check if every element in the local database is an instance of JASPAR_elem
        #check for the defined condition
        bool = all([(type(elem) == Objects.JASPAR_elem) for elem in database])
        self.assertTrue(bool, "Wrong types detected inside the DB!") 
    
    def test_no_duplicates(self): #define a test to check if there are any duplicates, as it should be
        uniques = set([elem.get_JASP() for elem in database]) #define the set of IDs, which are by definition unique since a set is created
        self.assertEqual(len(list(uniques)), len(database), "Duplicates detected inside the DB!") #if the number of unique IDs is equal to the number of elements in the database, I will have no duplicates
    
    def test_pd_dataframe(self): #define a test to check if all the PFM of the elements are pd.DataFrame objects
        import pandas as pd
        #check for the defined condition
        bool = all([(type(elem.get_MATRIX()) == pd.DataFrame) for elem in database])
        self.assertTrue(bool, "Not all the PFMs are of the right type!") 
    
    def test_right_ID(self): #define a test to check if all the elements have a correctly formatted ID, which means that it has to start by MA and the following part is numeric, for example MA1930.2
        #check for the defined condition
        bool = all([(elem.get_JASP().startswith("MA") and isinstance(float(elem.get_JASP()[2:]), float)) for elem in database])
        self.assertTrue(bool, "Not all the JASPAR_IDs are correctly formatted!")
    
    def test_DF_exception(self): #define a test to check if an expected exception is raised when needed. Please note that since most of the exceptions as caught by a try ... except block, 
                                 #I have to look for them by the associated error message, which is indeed unique
        import pandas as pd
        obj = database[0]
        self.assertTrue(obj.set_MATRIX("not_a_dataframe_for_sure").startswith("ERROR!"), "There is a problem when handling the JASPAR object") #here I am trying to set a non - pd.DataFrame as a PFM for a motif in the database, looking if the returned message is the ERROR message
    
    def test_consistent_order(self):  #define a test to check if all the elements have a consistently ordered PFM (i.e. with the same order for each of the bases)
        #check for the defined condition
        bool = all((elem.get_MATRIX().index.tolist() == ["A","C","G","T"]) for elem in database)
        self.assertTrue(bool, "Not all the bases in the PFM are consistently ordered")
    
#start the unittesting procedure, with verbosity = 2 for a nice output
if __name__ == '__main__':
    unittest.main(verbosity=2)
