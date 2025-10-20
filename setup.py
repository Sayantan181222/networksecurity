"""
The setup.py is is an essential part for packaging and distributing python projects. It is used by setuptools 
(or distutils in older python versions) to define configuration of the project, such as depedencies and metadata and etc.

"""


from setuptools import find_packages,setup
from typing import List



def get_requirements()->List[str]:
    """
    This function will return list of requirements 

    """

    requirement_lst : List[str] = []
    try:
        with open ('requirements.txt','r') as file:
            # read lines from the requirements.txt
            lines = file.readlines()
            # process each lines 
            for line in lines:
                # remove the spaces 
                requirement = line.strip()
                # iugnore empty lines and the -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
    
    except FileNotFoundError:
        print("requirements.txt file not found")


    return requirement_lst


setup(
    name = "NetworkSecurity",
    version = "0.0.1",
    author = "Sayantan",
    author_email = "sayantanman508@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements()
)

