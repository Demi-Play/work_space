import os

class Config:
    SECRET_KEY = 'IjQyMzQxZTJkMzA0ZGY2OWI1MjJlOGY4NWJlZTA5YjlkYWQyNzkyOGMi.zzzzUw.MFNmS9xSMzk2FRbmeZvb39z-0MU'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///workSpaceBase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False