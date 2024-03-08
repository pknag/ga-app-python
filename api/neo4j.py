from flask import Flask, current_app

from neo4j import GraphDatabase

"""
Initiate the Neo4j Driver
"""
def init_driver(uri, username, password):
    # Create an instance of the driver
    current_app.driver = GraphDatabase.driver(uri, auth=(username, password))

    # Verify Connectivity
    current_app.driver.verify_connectivity()

    return current_app.driver


"""
Get the instance of the Neo4j Driver created in the `initDriver` function
"""

def get_driver():
    return current_app.driver

"""
If the driver has been instantiated, close it and all remaining open sessions
"""

def close_driver():
    if current_app.driver != None:
        current_app.driver.close()
        current_app.driver = None

        return current_app.driver
