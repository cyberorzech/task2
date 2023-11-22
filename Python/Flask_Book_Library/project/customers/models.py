import re
from loguru import logger
from sys import stdout

from project import db, app

class ConfidentialInfoFlusher:
    def __repr__(self):
        # keys_blacklist = ["pesel", "street", "city"]
        keys_whitelist = ["name", "age", "id"]
        # flushed_info = {k: self.__dict__[k] for k in self.__dict__.keys() - {*keys_blacklist}}
        flushed_info = {k: self.__dict__[k] for k in self.__dict__.keys() if k in keys_whitelist}
        return str(flushed_info)


def obfuscate_message(message: str):
    """Obfuscate sensitive information."""
    SENSITIVE_INFO_REGEX_DICT = {
        "appNo": "AppNo: [A-Za-z0-9]{1,10}"
    }
    for index, regex in enumerate(SENSITIVE_INFO_REGEX_DICT.values()):
        try:
            pattern = re.compile(regex)
            match = pattern.search(message)
            result = message.replace(match.group(), f"{[*SENSITIVE_INFO_REGEX_DICT.keys()][index]}: ***")
        except AttributeError:
            continue
    return result

def formatter(record):
    record["extra"]["obfuscated_message"] = obfuscate_message(record["message"])
    return "[{level}] {extra[obfuscated_message]}\n{exception}"

logger.remove()
logger.add(stdout, format=formatter)



# Customer model
class Customer(ConfidentialInfoFlusher, db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    city = db.Column(db.String(64))
    age = db.Column(db.Integer)
    pesel = db.Column(db.String(64))
    street = db.Column(db.String(128))
    appNo = db.Column(db.String(10))

    def __init__(self, name, city, age, pesel, street, appNo):
        self.name = name
        self.city = city
        self.age = age
        self.pesel = pesel
        self.street = street
        self.appNo = appNo
        logger.success("Getting: " + str(self))

    def __repr__(self):
        return f"Customer(ID: {self.id}, Name: {self.name}, City: {self.city}, Age: {self.age}, Pesel: {self.pesel}, Street: {self.street}, AppNo: {self.appNo})"


with app.app_context():
    db.create_all()
