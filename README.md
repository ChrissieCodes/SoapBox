 Author: Christine A. Goodrich
 Date: 3/29/2022
 Purpose of the App: The app is designed to be a recommendation engine P2P instead of based on external prediction principles designed from centralized algorithms. 
 Starting by implementing the classes in the domain model from draw.io model in the Domain Model folder but removing the User and the Locations from the Model. The three Modules to start with will be the recommendation itself, the storage of the recommendation and the ranking of the recommendation. The process will be as follows, A recommendation is given by user/input, the recommendation is then stored and delivered at which point it is given a ranking 


# Cookies and Beer 
The design, creation, and testing of an app that introduces the idea of a decentralized >>buzz word<< recommendation engine. 

This test needs the following python packages installed
pytest
sqlalchemy
     create_engine
     .orm 
        sessionmaker,
        clear_mappers
        desc
       .session
            Session
requests
flask 
     Flask
     request
dataclasses
     dataclass
     asdict
__future__
     annotations
setuptools
     setup
abc 
     ABC
     abstractmethod
logging