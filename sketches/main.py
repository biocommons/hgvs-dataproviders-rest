# main.py

# Basic implementation of the Countries API example provided in:
# "Python and Rest APIs: Interacting with Web Services" at https://realpython.com/api-integration-in-python/#define-your-endpoints
# Starter code includes lines 10-25 along with GET and POST methods.
# DELETE, PUT, and PATCH are my own implementation.
# Note: Because I am just trying to make my first working implementation, there is no error handling included in any of these methods.

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

def _find_next_id():
    return max(country.country_id for country in countries) + 1

class Country(BaseModel):
    country_id: int = Field(default_factory=_find_next_id, alias="id")
    name: str = None
    capital: str = None
    area: int = None

countries = [
    Country(id=1, name="Thailand", capital="Bangkok", area=513120),
    Country(id=2, name="Australia", capital="Canberra", area=7617930),
    Country(id=3, name="Egypt", capital="Cairo", area=1010408),
]

def find_country(c_id : int):
    for country in countries:
        if country.country_id == c_id:
            return country
    
@app.get("/countries")
async def get_countries():
    return countries

@app.get("/countries/{item_id}")
async def get_country(item_id : int):
    return find_country(item_id)
    
@app.post("/countries", status_code=201)
async def add_country(country: Country):
    countries.append(country)
    return country

@app.delete("/countries/{item_id}", status_code=204)
async def remove_country(item_id : int):
    countries.remove(find_country(item_id))
    return
        
@app.put("/countries/{item_id}")
async def replace_country(country: Country, item_id : int):
    i = countries.index(find_country(item_id))
    countries[i] = country
    return country

@app.patch("/countries/{item_id}")
async def modify_country(country : Country, item_id : int):
    old_country = find_country(item_id)
    # Ideally, we do this with a loop. D: (how??)
    ###
    if(country.name == None):
        country.name = old_country.name
    if(country.capital == None):
        country.capital = old_country.capital
    if(country.area == None):
        country.area = old_country.area
    ###
    i = countries.index(old_country)
    countries[i] = country
    return country

    """
    Loop version, but doesn't filter out enough attributes
    for a in dir(country):
        if not a.startswith('_'):
            if a == None:
                country.a == old_country.a
    return country
    """