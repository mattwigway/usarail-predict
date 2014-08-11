# Declare database connection paramters here
from sqlalchemy import create_engine

def dbConnect():
    return create_engine('postgresql://dssgmatt:dssgmatt@localhost/dssgmatt', echo=True)
