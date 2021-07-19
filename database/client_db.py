import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logs.cfg_client_log as log_config
from common.decorators import transaction
from common.metacls import Singelton

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    contact = Column(String(50), index=True)

    def __init__(self, contact):
        self.contact = contact

    def __repr__(self):
        return f'<Contact({self.contact})>'


class MessagesHistory(Base):
    __tablename__ = 'messages_history'

    id = Column(Integer, primary_key=True)
    user_from = Column(String(50), index=True)
    recipient = Column(String(50), index=True)
    messages = Column(Text)
    create_at = Column(DateTime, default=datetime.utcnow())

    def __init__(self, user_from, recipient, messages):
        self.user_from = user_from
        self.recipient = recipient
        self.messages = messages
    
    def __repr__(self):
        return f'<MessagesHistory({self.recipient}, {self.messages})>'


class ClientStorage(metaclass=Singelton):
    DB = 'sqlite:///database/client_base.db3'

    def __init__(self, username=None):
        db = f'sqlite:///{username}_database.db3' if username else self.DB
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(db, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        session_factory = sessionmaker(bind=self.database_engine)
        self.session = session_factory()

    @transaction
    def add_contact(self, contact):
        contact = Contact(contact)
        self.session.add(contact)

    def get_contacts(self):
        return self.session.query(Contact).all()

    @transaction
    def add_message(self, user_from, recipient, messages):
        message = MessagesHistory(user_from, recipient, messages)
        self.session.add(message)

    def get_messages(self):
        return self.session.query(MessagesHistory).all()


def main():
    import random

    storage = ClientStorage()
    contact = f'Contact{random.randint(0, 100)}'

    storage.add_contact(contact)
    print(f'Contacts: {storage.get_contacts()}')

    storage.add_message(contact, 'Test msg')
    print(f'Messages: {storage.get_messages()}')


if __name__ == '__main__':
    main()