# Sigma Zero  - LabIACD 2nd Project Group 7 : Tomás, Vicente, Gonçalo e Anna


This is the LabIACD Group 7's second project AlphaZero repository. File structure, dependencies and necessary procedures to its workings are described below.

## File Structure:

### [game name] Folders:

    - These contain utilities and data with respect to each game setting. For each game, the fold structure as it is in this delivery version is needed for the automatization of training data storage process. There are subfolders for each board size with subfolders whithin that store board, policy and label files. (These are not included in the delivery because even though they ocuppy very little storage space unzipping or moving them takes too much time. Since these can be generated at anytime and are not particularly relevant to present, they're not included)

### Modelos:
    
    - Stored NN weights of last checkpointed attempt and best model for each game configuration. Some other files may be included with respect to relevnat model experiments or so.

### Main Folder Files:

    - agent* and server* files include programs that implement the proposed protocol for game-playing.
    - Attaxx.py and Go.py are the gamestate class files. These are not packaged in their own game folders because of the neeed to be imported and import other files. Such files that go under this condition are all kept in the main folder.
    - avaliar.py, optimizar.py and selfplay.py are the corresponding pipeline stage code, and auxiliary functions.
    - ioannina.py contains the Neural Network and model building functions.
    - MCTS.py is the MCTS-APV file.
    - treino.ipynb is a jupyter notebook where the training pipeline can be executed in a simple fashion.
    - delivery.ipynb is the final delivery notebook.

## Concerns regarding model building, training and execution:

    - Procedures needed to be executed in order to successfuly train the agent other than the especified folder structure already mentioned are documented in their respective files. The main files for execution will be treino.ipynb and server/agent files. The former requires some steps for initialization and the latter requires only the model weightes already included in this delivery package.

## Important Notices:

    - Information regarding model files and results are detailed in the final delivery notebook.