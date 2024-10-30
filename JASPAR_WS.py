
####### WEB-SERVICE #######

import sys
import os

current_path = os.path.dirname(os.path.abspath(__file__)) #obtaining the script's directory path
param_list = sys.argv #obtaining the input parameters list

class Input_parameter_Exception(Exception): #define an Exception for when no input parameter is defined
    def __str__(self):
        return "ERROR! Make sure you have inserted the required parameters!"

try:
    if len(param_list) < 2: #if the user inserted no arguments, the only one in the list is the script's name
        raise Input_parameter_Exception
    else:
        try:
            port_var = int(param_list[1]) #define the variable for the port used by the web service
        except ValueError as e:
            print("ERROR! The port number must be an integer!")
            sys.exit(1) #exit the script with an error code
except Input_parameter_Exception as e:
    print(str(e))
    sys.exit(1)

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import random
    import json
    import requests
    from statistics import mean
    from flask import Flask, jsonify, request
    sys.path.insert(0, './Pacchetto_JASPAR') #insert the path of the package in the list of paths used by python to import packages, in the first position
    from Pacchetto_JASPAR import DB_setup, Objects, sscore, from_dict #import the modules of the package
except ModuleNotFoundError:
    print("ERROR! Make sure you installed all dependencies!\nYou can install them all together using \"pip install -r\" giving as input the requirements.txt file you find in the folder")
    sys.exit(1)
except ImportError:
    print("ERROR! Make sure you installed all dependencies!\nYou can install them all together using \"pip install -r\" giving as input the requirements.txt file you find in the folder")
    sys.exit(1)
    
try:
    set_up = DB_setup.DB_setup() #Prepare the database before launching the Flask app! Please note that this is a list!
except requests.exceptions.ConnectionError as e: #If the user is not connected to the internet the setup of the database will fail!
    print("ERROR! Make sure you are connected to the Internet!")
    sys.exit(1)

app = Flask(__name__) #define the app

@app.route("/")
def central_hub(): #define a first function to list all the possible things the WS can do
    ascii_art = """ 
    
                  (   (            (                     
            (     )\ ))\ )   (     )\ )                  
        (   )\   (()/(()/(   )\   (()/(                  
        )((((_)(  /(_)/(_)((((_)(  /(_))                 
       ((_)\ _ )\(_))(_))  )\ _ )\(_))                   
      _ | (_)_\(_/ __| _ \ (_)_\(_| _ \                  
     | || |/ _ \ \__ |  _/  / _ \ |   /                  
      \__//_/ \_\|___|_|   /_/ \_\|_|_\                  
                                                         
                       (       (          (              
 (  (          (       )\ )    )\ )       )\ )  (        
 )\))(   '(  ( )\     (()/((  (()/((   ( (()/(  )\  (    
((_)()\ ) )\ )((_)     /(_))\  /(_))\  )\ /(_)(((_) )\   
_(())\_)(((_((_)_     (_))((_)(_))((_)((_(_)) )\___((_)  
\ \((_)/ | __| _ )    / __| __| _ \ \ / /|_ _((/ __| __| 
 \ \/\/ /| _|| _ \    \__ | _||   /\ V /  | | | (__| _|  
  \_/\_/ |___|___/    |___|___|_|_\ \_/  |___| \___|___| 
                                                         
        Made -with love- by Gabriele Oliveto
    
    """
    resp = "\nWelcome to this RESTful JASPAR Web Service! You can interact with this local JASPAR Database in different ways:\n\n - GET a specific DNA motif or ALL stored motifs from the Database\n - UPDATE an existing motif\n - ADD a new motif to the Database\n - REMOVE an existing motif (even all of them) from the Database\n - GET the logo of the motifs you're interested in\n - SUBMIT a sequence of length L and retrieve the similarity scores compared to other motifs' of length L \n - GET basic Database statistics and length distribution barplot\n\n"
    return "\n" + ascii_art + resp

@app.route("/test") #run the UnitTest to assess the goodness of the local database
def run_tests():
    os.system(f'python {current_path}/tests/test_db_setup.py') #run the command to excecute the script in a subshell 
    return "UnitTest procedure correctly performed!"

@app.route("/stats")
def get_stats(): #define a function to obtain basic statistics about the database
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        #here I am gathering basic information about the database, such as minimum motif length, maximum motif length, average length, number of motifs...
        length_DB = [elem.get_LENGTH() for elem in set_up]
        number_stored_motifs = len(set_up)
        shortest_motifs = min(length_DB)
        number_shortest_motifs = len([elem for elem in set_up if elem.get_LENGTH() == shortest_motifs])
        longest_motifs = max(length_DB)
        number_longest_motifs = len([elem for elem in set_up if elem.get_LENGTH() == longest_motifs])
        average_motif_length = mean(length_DB)
        return f'\nNumber of stored motifs: {number_stored_motifs}\nShortest motif(s) is {shortest_motifs} bp long ({number_shortest_motifs} stored)\nLongest motif(s) is {longest_motifs} bp long ({number_longest_motifs} stored)\nAverage motif length is: {average_motif_length}\n\n'

@app.route("/stats/plot")
def get_stats_plot(): #define a function to plot the motif length distribution using matplotlib, saving it in the IMAGES plot
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        length_DB = [elem.get_LENGTH() for elem in set_up]
        longest_motifs = max(length_DB)
        plot = []
        for i in range(1,longest_motifs+1):
            lis = len([elem for elem in set_up if len(elem.get_CONSENSUS()) == i])
            plot.append(lis)
        plt.figure() #create a new figure
        plt.bar(range(1,longest_motifs+1), plot, color = "green", edgecolor = "black")
        plt.xlabel("Motif Length")
        plt.ylabel("Absolute Frequency")
        plt.title("Motifs length distribution")
        plt.savefig(f"{current_path}/JASPAR_Images/barplot.png", dpi = 350) #save the created plot in the IMAGES folder inside the main folder
        return "Barplot has been successfully saved as a .png file in the Images folder!"

@app.route("/all")
def get_all(): #define a function to retrieve all the database elements
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        lis = [elem.__str__() for elem in set_up] #NOTE: The database elements are self defined objects, so here I am returning their .__str__
        return "\n\n".join(lis)

@app.route("/var/all")
def get_var_all(): #define a function to retrieve the JSON strings for all the elements in the database, in order to perform the same thing as before, but also via a client script
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        lis = [elem.to_dict() for elem in set_up] #the method .to_dict() converts the element to a dictionary, which is serializable to a JSON string
        return jsonify(lis)

@app.route("/<ID>")
def get_specific(ID): #define a function to retrieve a specific element in the database , if present
    lis = [elem.__str__() for elem in set_up if elem.get_JASP() == ID] #again, here I am returning the element's .__str__()
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(lis) == 0:
        return "No such motif is stored in the Database, try with another JASPAR_ID!"
    else:
        return "\n\n".join(lis)

@app.route("/var/<ID>")
def get_var_specific(ID): #define a function to retrieve the JSON strings for a specific element in the database, if present
    lis = [elem.to_dict() for elem in set_up if elem.get_JASP() == ID] 
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(lis) == 0:
        return "No such motif is stored in the Database, try with another JASPAR_ID!"
    else:
        return jsonify(lis[0])
    
@app.route("/TF/<TF_name>")
def get_specific_TF(TF_name): #define a function to retrieve a specific element in the database , if present
    lis = [elem.__str__() for elem in set_up if elem.get_TF_name() == TF_name] #again, here I am returning the element's .__str__()
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(lis) == 0:
        return "No such motif is stored in the Database, try with another TF_name!"
    else:
        return "\n\n".join(lis)

@app.route("/TF/var/<TF_name>")
def get_var_specific_TF(TF_name): #define a function to retrieve the JSON strings for a specific element in the database, if present
    lis = [elem.to_dict() for elem in set_up if elem.get_TF_name() == TF_name] 
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(lis) == 0:
        return "No such motif is stored in the Database, try with another TF_name!"
    else:
        return jsonify(lis)

@app.route("/random")
def get_random(): #define a function to retrieve a random element in the database
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        selected_elem = random.choice(set_up)
        return selected_elem.__str__()

@app.route("/var/random")
def get_var_random(): #the function works in the same way as the one above, but returining the JSON string
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        selected_elem = random.choice(set_up)
        return jsonify(selected_elem.to_dict())

@app.route("/logo/<ID>")
def get_logo(ID): #define a function to create the logo of a specific motif, using a specific method in the class, computing the Information Content for each base in each position, further explanation in the commented script of the Objects module of the package
    lis = [elem for elem in set_up if elem.get_JASP() == ID]
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(lis) == 0:
        return "No such motif is stored in the Database, try with another JASPAR_ID!"
    else:
        lis[0].create_logo() #the method creates an image that is saved in the JASPAR_Images folder
        return "Logo has been successfully saved as a .png file in the Images folder!"

@app.route("/sscore/<sequence>")
def get_sscore(sequence): #define a function to obtain all the similarity scores of motifs of length L, given an input sequence of the same length L
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        try:
            if any(char not in ["A","C","T","G"] for char in sequence): #if there are characters other than the standard ones for the JASPAR format (only A,C,G,T are considered)
                raise Objects.Character_Exception
            else:
                res = sscore.get_sequence_scores(sequence, set_up) #call the function to obtain the scores
                if res == "There is no stored motif of such length!":
                    return "\n" + res + "\n\n"
                else:
                    return "\n" + "JASPAR_ID\tConsensus\tScore\n\n"+ res + "\n\n"
        except Objects.Character_Exception as e:
            return str(e)

@app.route("/all", methods = ["DELETE"])
def delete_all(): #define a function to delete all elements from the database
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        set_up.clear()
        return "All motifs have been removed from the database!"

@app.route("/<ID>", methods = ["DELETE"])
def delete_specific(ID): #define a function to delete a specific element from the database, if present
    if len(set_up) == 0:
        return 'Database is empty!'
    else:
        selected_elem = [elem for elem in set_up if elem.get_JASP() == ID]
        if len(selected_elem) == 0:
            return "No such motif is stored in the Database, try with another JASPAR_ID!"
        else:
            set_up.remove(selected_elem[0]) #the element in remove from the actual list
            return f'\n{selected_elem[0].__str__()}\n{selected_elem[0].get_JASP()} has been removed from the database\n\n'

@app.route("/add", methods = ["POST"])
def add_specific(): #define a function to add a specific element to the database
    elem = request.get_json() #recieve the request as a dictionary
    accepted_types = [str, list]
    required_fields = sorted(["JASPAR_ID","TF_name","PFM"])
    try:
        if required_fields == sorted(list(elem.keys())): #if the fields in the dictionary are exactly the defined ones
            if type(elem["PFM"]) not in accepted_types: #if the PFM is of another type raise a Type Error, the idea is that the PFM has either to be a string or a list
                raise TypeError
            if type(elem["PFM"]) == str: #if the PFM is a string
                elem["PFM"] = json.loads(elem["PFM"]) #convert it to a list
            if len(elem["PFM"]) != 4: #since we have one row for each base, we need exactly 4 elements, that are dictionaries, for the list
                raise Objects.PFM_Exception
            if len(set(len(obj.keys()) for obj in elem["PFM"])) != 1: # if the length of the set composed of the length of the keys in each dictionary is not 1, then I inserted dictionaries of different lengths, while I need each possible position to have a value
                    raise Objects.Length_Exception
            else:
                elem["JASPAR_ID"] = elem["JASPAR_ID"].replace(" ", "_") #replace spaces with underscores in order to allow for proper object calling 
                elem["TF_name"] = elem["TF_name"].replace(" ", "_")
                if str(elem["JASPAR_ID"]) not in [elem.get_JASP() for elem in set_up]: #check if the element you want to insert is already present
                    if elem["JASPAR_ID"] != "" and elem["TF_name"] != "": #prevent the user from setting empty names
                        elem = from_dict.from_dict(elem) #convert the dictionary, back into the object
                        set_up.append(elem) 
                        return f"\n{elem.__str__()}\n{elem.get_JASP()} has been added to the database!\n\n"
                    else:
                        raise NameError
                else:
                    return f'{elem["JASPAR_ID"]} is already present in the database!'
        else:
            raise Objects.Dictionary_Exception

    #catch all the exceptions
    except TypeError as e:
        return "ERROR! Make sure the PFM is of the correct type!"
    except NameError as e:
        return "ERROR! Make sure that both the JASPAR_ID and TF_name fields are not empty!"
    except Objects.PFM_Exception as e:
        return str(e)            
    except Objects.Dictionary_Exception as e:
        return str(e)
    except Objects.Length_Exception as e:
        return str(e)
    except json.decoder.JSONDecodeError as e: #the PFM can't just be any string, or a DecodeError is raised
        return "ERROR! Make sure that the PFM is correctly formatted, check the documentation for details!"
    except ValueError as e: #the PFM list of dictionaries has to be correctly formatted, even in the values of the keys
        return "ERROR! Make sure that the PFM dictionaries are progressive numbers starting from 1! Check the documentation for details!"
    except Exception as e: #other unexpected exceptions may occurr, that I want to catch
        return "ERROR! Something unexpected went wrong!"
    
@app.route("/<ID>", methods = ["PUT"])
def update_specific(ID):
    selected_elem = [elem for elem in set_up if elem.get_JASP() == ID] #select the element to be updated
    accepted_types = [str, list]
    if len(set_up) == 0:
        return 'Database is empty!'    
    elif len(selected_elem) == 0:
        return "No such motif is stored in the Database, try with another JASPAR_ID!"
    else:
        selected_elem = selected_elem[0]
        former_elem_id = selected_elem.get_JASP() #save former element's ID for rollback
        former_elem_TF = selected_elem.get_TF_name() #save former element's TF_name for rollback
        former_elem_PFM = selected_elem.get_MATRIX() #save former element's PFM for rollback
    to_be_updated = request.get_json() #get the request as a dictionary
    try:
        for k,v in to_be_updated.items():
            if k == "JASPAR_ID":
                if str(v) == "": #prevent the user from setting empty names
                    raise NameError
                v = v.replace(" ", "_") #replace spaces with underscores in order to allow for proper object calling 
                if str(v) in [elem.get_JASP() for elem in [elem for elem in set_up if elem != selected_elem]]: #check if the ID I want to set already exists on other motifs
                    return "Cannot set the same unique identifier for two motifs!"
                else:
                    selected_elem.set_JASP(v) #use the setter to define the ID
            elif k == "TF_name":
                if str(v) == "": #prevent the user from setting empty names
                    raise NameError
                v = v.replace(" ", "_") #replace spaces with underscores in order to allow for proper object calling 
                selected_elem.set_TF_name(v) #use the setter to define the TF_name
            elif k == "PFM":
                if type(v) not in accepted_types:
                    raise TypeError
                if type(v) == str: #if the PFM is a string
                    v = json.loads(v) #convert it to a list
                if len(v) != 4: #since we have one row for each base, we need exactly 4 elements (dictionaries) for the list
                    raise Objects.PFM_Exception
                if len(set(len(elem.keys()) for elem in v)) != 1: # if the length of the set composed of the length of the keys in each dictionary is not 1, then I inserted dictionaries of different lengths, while I need each possible position to have a value
                    raise Objects.Length_Exception
                data_frame = pd.json_normalize(v) #convert the elements into a pd.DataFrame. NOTE: the function json_normalize works in a records oriented way (so each dictionary in the list is a row)
                data_frame.index = ["A","C","G","T"] #NOTE: the order of the bases is harcoded throughout the whole script, since it refers to the JASPAR format 
                data_frame.columns = ["" for col in data_frame.columns] #set empty spaces as the names of the columns
                selected_elem.set_MATRIX(data_frame) #use the setter in order to set the matrix of the object
            else: #if the keys are not exactly the ones I defined
                raise Objects.Dictionary_Exception       
        return f'\n{selected_elem.__str__()}\n{former_elem_id} has been updated!\n\n'


    #catch all the exceptions and perform a rollback. 
    #I organized the function in an iterative way, so the values are updated just after their checks. 
    #In order to avoid a partial update a rollback is needed for the ID, TF_name and the PFM 
    
    
    except NameError as e:
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return "ERROR! Make sure that both the JASPAR_ID and TF_name fields are not empty!"
    except TypeError as e:
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return "ERROR! Make sure the PFM is of the correct type!"
    except Objects.PFM_Exception as e:
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return str(e)
    except Objects.Dictionary_Exception as e:
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return str(e)
    except Objects.Length_Exception as e:
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return str(e)
    except json.decoder.JSONDecodeError as e: #the PFM can't just be any string, or a DecodeError is raised
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return "ERROR! Make sure that the PFM is correctly formatted, check the documentation for details!"
    except ValueError as e: #the PFM list of dictionaries has to be correctly formatted, even in the values of the keys
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM) 
        return "ERROR! Make sure that the PFM dictionaries are progressive numbers starting from 1! Check the documentation for details!"
    except Exception as e: #other unexpected exceptions may occurr, that I want to catch
        selected_elem.set_JASP(former_elem_id)
        selected_elem.set_TF_name(former_elem_TF)
        selected_elem.set_MATRIX(former_elem_PFM)
        return "ERROR! Something unexpected went wrong!"
 
 
#Define a set of errorhandler functions to manage error codes related to the Web-Service, since those types of error work differently from regular exceptions 


@app.errorhandler(400) #Request is wrongly formatted
def handle_bad_request(error):
    return "ERROR! Something is wrong with the formatting of the request!"
 
@app.errorhandler(404) #URL is not found
def handle_content_type(error):
    return "ERROR! The URL you requested has not been found!"

@app.errorhandler(405) #wrongly typed URL
def handle_method_not_allowed(error):
    return "ERROR! Something is wrong with the URL you typed! Are you using the right method?"
    
@app.errorhandler(415) #The option -H "Content-Type: application/json" is missing or wrongly typed
def handle_content_type(error):
    return "ERROR! Remember to specify or correctly write the option -H \"Content-Type: application/json\""


if __name__ == '__main__': #Start the Flask application
    app.run(host = "127.0.0.1", 
            port = port_var, #the port the program uses is defined at the beginning of the script and is an input parameter
            debug = True)
