
# **JASPAR Web Service Documentation**

The python project I decided to work on asked to develop a RESTful Web Service that granted the user to interact with the [JASPAR motifs Database](https://jaspar.elixir.no/), allowing for  the excecution of some basic tasks, which will be discussed in this documentation file. 
Here you will find an - hopefully enough - exhaustive  explanation on how the project is structured and how its components work.

## **_<u>Introduction</u>_**

Inside this folder - together with the **_README_** files - you will also find:

 - The **_Pacchetto_JASPAR_** folder, which is the Python package I created!
 - The **_JASPAR_WS.py_** file, which is the main script for the application!
 - The **_Images_** folder, in which all images will be dowloaded
 - The **_tests_** folder, containing the UnitTest script!
 - The 	**_requirements.txt_** file, containing all the package dependencies 
 
All the components are designed in order to grant a user-friendly experience for the interaction with a local copy of the JASPAR motifs Database. Each motif stored in the Database is characterised by three essential information:

- The **Jaspar_IDs**, which is the unique identifier for each motif (e.g. MA1930.2)
- The **corresponding TF name** (e.g. CTCF)
- The **P**robability **F**requency **M**atrix (**PFM**)

The application allows for different types of interactions with the locally stored motifs:

 - **GET** a specific DNA motif or ALL stored motifs from the Database (or even RANDOM ones)
 - **UPDATE** an existing motif
 - **ADD** a new motif to the Database
 - **REMOVE** an existing motif (or even all of them) from the Database
 - **SUBMIT** a sequence of length L and **GET** the similarity scores compared to other motifs of length L
  - **GET** the sequence logo of the motifs you're interested in
 - **GET** basic Database statistics and length distribution barplot of the motifs

## **_<u>Python package</u>_**

### _<u>How to install the package</u>_

In order to tidy up the main script containing the Flask application I decided to create a python package. The package encloses the main functions and objects I used to handle the information contained in the JASPAR Database and performs tasks that are useful for the Web Service application. 

Since the package is a local one, the installation step using "pip" or "pip3" commands is not needed. However proper attention must be paid to its dependencies.

In order to properly install dependencies, the **_requirements.txt_** file will be used and the procedure to install them is straight forward:

	pip install -r ./path_to_folder/requirements.txt
	
With this command all the dependencies listed in the file will be installed.

### _<u>Package modules</u>_

The package I created is composed of different modules. To be more specific, there is generally one module for each function and one module for the objects I created. The modules are explained in the following paragraphs and the commented version of the scripts are available inside the **_Pacchetto_JASPAR_** folder.

#### _DB_setup module_

This module contains the **DB_setup** function, which creates the local Database,  in which all the motifs are stored. The function requests [data](https://jaspar.elixir.no/download/data/2024/CORE/JASPAR2024_CORE_non-redundant_pfms_jaspar.txt) directly from the JASPAR Database, which provides a .txt file in [JASPAR format](https://jaspar.elixir.no/docs/). The file is then processed in order to create consistent and correct **Jaspar_elem** objects, stored inside a list.

#### _Objects module_

A module containing all the self defined objects has been created. The module contains several Exceptions, defined to handle different possible unwanted scenarios, but the main core of the module - and of the package in general - is the **Jaspar_elem** object.

- **<u>Jaspar_elem</u>**

The object has been created in order to properly treat all motifs stored in the database. Several methods for the class have been devised in order to grant an easy interaction with the objects. 

A set of getters has been defined in order to easily retrieve the attributes:

- **get_JASP**, which retrieves the JASPAR_ID
- **get_TF_name**, which retrieves the associated TF name
- **get_CONSENSUS**, which retrieves the motif's consensus sequence (i.e. the most frequent base at each position)
- **get_LENGTH**, which retrieves the motif's length
- **get_MATRIX**, which retrieves the motif's PFM
- **get_NORM_MATRIX**, which retrieves the motif's normalized PFM

A set of setters has also been defined in order to set the object's attributes:

- **set_JASP**, which sets the JASPAR_ID
- **set_TF_name**, which sets the associated TF name
- **set_MATRIX**, which not only sets the PFM, but also sets the **length**, **consensus sequence** and the **normalized matrix** attributes of the motif. This allows for a more compact and controlled handling of the motifs' main attributes when adding a new motif or updating an existing one, since all the attributes deriving from the PFM are accordingly set. 

The PFM is designed to be a pd.DataFrame. Rows represent different bases and the columns represent the particular position in the motif. Please note that the order of the bases inside the PFM is always the same (i.e. A, C, G, T) according to the JASPAR documentation. For more details check the _Unit-Testing_ section. Since the expected type for the PFM is pd.Dataframe, proper exceptions will be raised if this condition is not met.

When an instance of Jaspar_elem is created, all setters are called in the constructor of the object (**\_\_init\_\_**)

Other important methods have been defined:

- **find_consensus**, that defines the consensus  sequence of the motif
- **to_dict**, which converts the Jaspar_elem instance into a dictionary, composed of three main items (key - value pairs):

	- **JASPAR_ID**
	- **TF_name**
	- **PFM**, containing a JSON representation of the PFM, structured as a list of dictionaries, in a records oriented way (one dictionary per row).  The list contains 4 dictionaries, one for each base, ordered according to the JASPAR documentation (i.e. A, C , G, T). Each of the items in the dictionary will have keys corresponding to a progressive number ranging from 1 up to the length of the motif, and values displaying the count of that particular base at that specific position of the motif

- **create_logo**, which uses the logomaker package to retrieve the [motif logo](https://drive.google.com/file/d/1jiAof_SPiWHWQwY3rV0c7u3S6h_3zwSy/view?usp=drive_link). The Information Content for each position is computed as 2 - Shannon's Entropy. The proportional height of each of the bases in the logo is then computed multiplying the Information content of that position by the relative frequency of the base at that position. The logo is finally saved as a .png image (_named as the **Jaspar_ID**_)  in the **_Images_** folder.

Finally the **\_\_str\_\_** is defined, in order to provide a pretty printed and more readable graphical representation of the motif
		

 - **Exceptions**

	- **Dictionary_Exception** is raised when wrong keys are used when adding or updating a Jaspar_elem object in the database. The correct keys are:
	
		- **JASPAR_ID**
		- **PFM**
		- **TF_name**

	- **Dataframe_Exception**, which is raised when trying to set as a PFM a non pd.DataFrame object. 

	- **Jaspar_elem_Exception**, raised whenever a Jaspar_elem object is needed for some kind of task, but a different type of object is found instead.

	- **Character_Exception**, raised when bases different from the standard ones (e.g.  A, C, G, T) are detected in the input sequence when retrieving the confidence scores.

	- **PFM_Exception** is raised when adding a Jaspar_elem object or updating its PFM, if the list containing the records (that are dictionaries) of the PFM (or its JSON representation) has a length different from 4 (one record for each of the bases)

	- **Length_Exception** is raised when adding a Jaspar_elem object or updating its PFM, if the dictionaries inside the list containing the records of the PFM (or its JSON representation) are of different lengths (which means that a pd.DataFrame with rows of different length would be created)

#### _from_dict module_

This module contains the **from_dict** function, which takes as input a **dictionary representation** of a Jaspar_elem object and converts it back into a proper Jaspar_elem object. All the attributes are automatically taken care of, even though only the **Jaspar_ID**, **TF_name** and **PFM** are required.

Please note that, since this function is called when adding the element to the database, proper controls are made, in order to avoid unwanted results and proper Exceptions may be raised. For more details on how to correctly add elements to the Database, look at the _Web Service section_ (_Add a new element to the database paragraph_)

#### _sscore module_

This module actually contains 2 functions, called **get_single_score** and **get_sequence_scores**. Thanks to these function the computation of the similarity scores is allowed. In particular, given an input DNA sequence of length L, the functions compute the similarity scores for all the motifs of the same length L. 

Given the input sequence, the similarity score is computed based on the relative frequencies of the corresponding base at a specific position of the motif. In particular the multiplication of the relative frequencies is computed, representing as a score the global probability of having that particular sequence. 

One function (**get_single_score**) computes the similarity score for one single motif, given an input DNA sequence. The other one (**get_sequence_scores**)  creates a report - applying the first function to all motifs of length L stored in the database -  and returns the **Jaspar_ID**, the **consensus sequence** of the motif and the **similarity scores**. 

Please note that these functions have been created only considering the standard DNA bases (e.g. A, C, T, G), since they are the only ones present in the JASPAR format for DNA motifs. If other letters are inserted for the input sequence when typing the link, a proper exception will be raised.

## _**<u>Web Service Application</u>**_

### _<u>How to launch the Web Service application</u>_

In order to start the Web Service application, the main script (i.e. **_JASPAR_WS.py_**) must be excecuted. The user is required to have an Internet connection and to specify the port number. The internet connection is needed in order to request data from the JASPAR Database, whereas the port number is left to be specified in order to allow the user to choose it.

The application can be launched using the command line, by typing:
		
	python ./path_to_folder/JASPAR_WS.py <port_number>

Please, remember that the \<port_number> argument is mandatory and MUST be an integer.
When the Web Service application is started, the local Database containing all the motifs - stored as Jaspar_elem objects - is created and will be ready to use.

### _<u>How to call the functions</u>_

The main application uses functions and Objects created in the package in order to operate and provide the user a complete experience with the local JASPAR Database. All the actions that the user is allowed to perform are accessible using links that are routed to the corresponding functions, operating on the Database and its elements. 
Here is an example of a link:

	http://127.0.0.1:<port_number>/specific_link	

For starters, a central hub for the local Web Service can be invoked by simply typing:

	curl http://127.0.0.1:<port_number>/

this will simply display the logo of the application - made using ASCII art - and the main features provided by the Web Service.

In the next paragraphs you will find an explanation of the main features of each function, how they can be called and a sound explanation of how these functions work.

### _<u>Retrieve one or more elements from the Database</u>_

In order to retrieve the elements that are stored in the Database, different functions have been created. The functions can be divided into two main categories:

- Functions used to retrieve the **string representation** (i.e. the \_\_str\_\_) of each **Jaspar_elem**
- Functions used to retrieve the **JSON** representation of each Jaspar_elem, that will include **/var/** in the link routed to them

This main categorization has been made in order to both provide a pretty printed output for each of the elements - returning the string representation of the motif - and a more usable JSON string for the elements, that can be easily  handled in a Python script working as a Client.

For each of this categories we find three functions, that can be accessed through these links:

- Retrieve **ALL** the elements in the Database

		curl  http://127.0.0.1:<port_number>/all
	    curl  http://127.0.0.1:<port_number>/var/all

- Retrieve a **SPECIFIC** element in the Database

		curl  http://127.0.0.1:<port_number>/<ID>
	    curl  http://127.0.0.1:<port_number>/var/<ID>
	    
- Retrieve a **RANDOM** element in the Database

		curl  http://127.0.0.1:<port_number>/random
	    curl  http://127.0.0.1:<port_number>/var/random
 
### _<u>Remove one (or even all) element from the Database</u>_

Functions to remove one element (or all of them) from the local Database have been devised, easily accessible using the following links.

- Remove **ONE** single element from the local Database
		
		curl -X DELETE http://127.0.0.1:<port_number>/<ID>

- Remove **ALL** elements from the local Database

		curl -X DELETE http://127.0.0.1:<port_number>/all


### _<u>Add a new element to the database</u>_

The user is allowed to add new elements to the Database. An example is provided below and some key aspects will be later discussed:

    curl -H "Content-Type:application/json" -X POST -d 
    "{\"PFM\":
     [{\"1\":34,\"2\":16,\"3\":22,\"4\":34,\"5\":53,\"6\":29,\"7\":10},
     {\"1\":23,\"2\":85,\"3\":60,\"4\":7,\"5\":90,\"6\":7,\"7\":97},
     {\"1\":45,\"2\":16,\"3\":34,\"4\":30,\"5\":50,\"6\":45,\"7\":10},
     {\"1\":23,\"2\": 55,\"3\":0,\"4\":25,\"5\":25,\"6\":10,\"7\":24}], 
     \"JASPAR_ID\" : \"trial_for_documentation\",
     \"TF_name\" : \"trial_for_documentation\"}" http://127.0.0.1:5000/add
    
The JSON string sent to the Web Service has to contain **all the main fields** used by the Jaspar_elem to set its attributes, for more details look at the _Python Package section_ (_Objects paragraph_).

The PFM has to be written as a JSON representation of a **list of dictionaries**. Each dictionary represents a row of the PFM, corresponding to the occurrencies of a particular base across all positions of  the motif. Each dictionary in the PFM field MUST contain **progressive numbers** from 1 up to the length of the motif as keys, corresponding to the position of the base in the motif.

The order of the dictionaries inside the list follows the **alphabetical order** (e.g. A, C, G, T), as indicated in the [JASPAR documentation](https://jaspar.elixir.no/docs/).


Please note that controls are made in order to avoid unwanted situations and proper Exceptions will be raised if the user writes the request in a wrong way. Some common errors may be:

- Forgetting that the keys of the dictionaries MUST be progressive numbers from 1 up to the length of the motif
- Trying to insert dictionaries of different lengths
- Inserting empty keys or values
- Forgetting to put the -H "Content-Type:application/json" option
- Inserting wrongly typed keys
- Forgetting to insert all required keys

Please note that the user can insert the Jaspar_ID, regardless of the rules used for the motifs' IDs in the official database (MA followed by numbers, e.g. MA1930.2). If the user decides to insert the Jaspar_ID - or the TF_name - including some spaces the program will automatically fix it by replacing spaces with underscores (e.g. "trial for documentation" will become "trial_for_documentation"). 

Remember that the Jaspar_ID is an unique identifier, and if a non-unique ID is encountered the application will refuse to add the motif to the Database.

If no error is encoutered the _**from_dict**_ function is called and a **new Jaspar_elem** instance is added to the Database.
    
### _<u>Update an existing element in the database</u>_

Similar principles apply for updating elements stored in the Database, except for one small difference. The program has been developed for the user to be able to modify **up to each cell in the PFM** of the motif. An example is provided below:

    curl -H "Content-Type:application/json" -X PUT -d 
    "{\"PFM\":
    [{\"1\":34,\"2\":16,\"3\":22,\"4\":34,\"5\":53,\"6\":29,\"7\":10},
    {\"1\":23,\"2\":85,\"3\":60,\"4\":7,\"5\":90,\"6\":7,\"7\":97},
    {\"1\":45,\"2\":16,\"3\":34,\"4\":30,\"5\":50,\"6\":45,\"7\":10},
    {\"1\":23,\"2\": 55,\"3\":0,\"4\":25,\"5\":25,\"6\":10,\"7\":24}], 
    \"JASPAR_ID\" : \"trial_for_documentation\",
    \"TF_name\" : \"trial_for_documentation\"}" http://127.0.0.1:5000/<ID>

The motif with Jaspar_ID corresponding to \<ID> will be updated. 
The main concepts regarding the update of a motif are the same as the ones stated in the previous paragraph. The only difference is:

- Here, the user can choose to **only update some features of the motif**, so not all standard fields will be required in the JSON representation of the Jaspar_elem in the request.

Please note that, if errors are detected, during the update of a motif, proper Exceptions will be raised and a rollback will be performed. The most common errors the user can make are the same as the previous paragraph.

If no error is encoutered, Jaspar_elem __setters__  are called and the Jaspar_elem stored in the Database will be updated.

### _<u>Similarity score</u>_

By typing the following link

	curl http://127.0.0.1:<port_number>/sscore/<sequence>

The user will be able to compute the similarity scores for all the motifs of the same length of the input \<sequence>. As stated in the _Python Package section_ (_sscore module paragraph_) a report is displayed, returning some informations about the motifs, including the similarity scores. 


### _<u>Miscellaneous functions</u>_

#### _Generate Motif Logo_

By using the following link

	curl http://127.0.0.1:<port_number>/logo/<ID>

the **.create_logo** method for the Jaspar_elem object having a **Jaspar_ID** corresponding to \<ID> is created. The image is saved as a .png (_named as the **Jaspar_ID**_)  in the **_Images_** folder. For more details regarding the method for the motifs logo generation, look at the _Python Package section_ (_Objects paragraph_).

#### _Get Statistics of the local Database_

By using the following link
		
	curl http://127.0.0.1:<port_number>/stats
		
the user can retrieve basic statistics of the local Database, such as:

- **Number** of currently stored **motifs**
- Length of the **shortest motifs** (and their number inside the Database)
- Length of the **longest motifs** (and their number inside the Database)
- **Mean length** of the motifs inside the Database

This function wants to give the user an immediate idea of the characteristics of the motifs stored in the Database.

#### _Get a Barplot of motifs length distribution_ 

By using the following link
		
	curl http://127.0.0.1:<port_number>/stats/plot
		
the user can retrieve a barplot of the motifs length distribution, generated using Matplotlib. The image is saved as a .png (named _barplot_) in the **_Images_** folder. This barplot wants to give a quick visual representation of the data stored in the Database.

The barplot should look like [this](https://drive.google.com/file/d/1qIsnJNgoAj7NqrHMlFOrDLK2p7FiwcDh/view?usp=drive_link) even though the shape of it may change if some updates in the PFM are made or if some new motifs are added.

### _<u>Error Handlers</u>_

A set of errorhandlers has been defined in order to cope with some possible errors in the Web Service context. The functions handle some common error the user can make, mostly related to errors in the typing of the request. Some common errors may be:

- Generic **typing errors** inside the commands
- Making a request using the **wrong method** (e.g. **DELETE** instead of **GET**)
- Requesting a **URL** that **does not exist**
- Forgetting to type the option **-H "Content-Type: application/json"** when adding or updating an element in the Database

 These errorhandler functions allow for a better reaction of the Web Service application to unexpected requests. 

## _**<u>Unit-Testing</u>**_

Some UnitTests have been implemented in order to check for some key aspects in the context of the local Database creation. All the tests can be excecuted by simply using the following link:

	curl http://127.0.0.1:<port_number>/test
	
This link calls the function that runs the Unittesting script in the _tests_ folder. 
The following tests have been devised:
- Check for the **completeness of the database**
- Check for the **uniqueness of** the **Jaspar_IDs**
- Check if **all** the database **elements are** instances of **Jaspar_elem**
- Check if **all** the **PFMs** of the Jaspar_elem **are pd.DataFrames** 
- Check for a correct **formatting of the Jaspar_IDs**, when the local Database is initialized
- Check for the **correct raising of an Exception**, when wrongly setting an attribute of the Jaspar_elem objects
- Check for the **consistent order of the bases in the PFM** throughout the whole local Database. According to the [JASPAR format](https://jaspar.elixir.no/docs/), the order of the bases in the PFM must be **A, C, G, T**. 

>Made -with love- by Gabriele Oliveto
