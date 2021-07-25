from common.request_body import Room
import logging
import threading
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, __version__
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logs.cfg_server_log as log_config
from common.decorators import transaction

from icecream import ic

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<User({self.name})>'

    def __str__(self):
        return self.name


class UserOnline(Base):
    __tablename__ = 'online'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    fileno = Column(Integer)

    def __init__(self, user_id, fileno):
        self.user_id = user_id
        self.fileno = fileno


class RoomName(Base):
    __tablename__ = 'room_name'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    create_at = Column(DateTime)

    def __init__(self, name):
        self.name = name
        self.create_at = datetime.utcnow()

    def __repr__(self):
        return f'<RoomName({self.name})>'


class Rooms(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('room_name.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id


class LoginHistory(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column(DateTime)
    ip = Column(String)

    def __init__(self, user_id, time, ip):
        self.user_id = user_id
        self.datetime = time
        self.ip = ip


class Contact(Base):
    __tablename__ = 'contacts'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, user_id, contact_id):
        self.user_id = user_id
        self.contact_id = contact_id


class UserStat(Base):
    __tablename__ = 'user_stats'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    mes_sent = Column(Integer, default=0)
    mes_recv = Column(Integer, default=0)

    def __init__(self, user_id):
        self.user_id = user_id
        self.mes_recv = 0
        self.mes_sent = 0


class ServerStorage:
    DB = 'sqlite:///database/server_base.db3'
    sessions = {}

    def __init__(self):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(self.DB, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        self.session_factory = sessionmaker(bind=self.database_engine)
        self.session.query(UserOnline).delete()
        self.session.commit()

    @property
    def session(self):
        thread = threading.current_thread().name
        if thread in self.sessions:
            return self.sessions[thread]
        else:
            session = scoped_session(self.session_factory)()
            self.sessions[thread] = session
            return session

    @transaction
    def register_user(self, username):
        user = User(username)
        self.session.add(user)
        return user

    def get_users(self):
        return self.session.query(User).all()

    def get_user_by_name(self, username):
        return self.session.query(User).filter_by(name=username).first()
    
    def get_user_by_id(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()

    @transaction
    def login_user(self, username, ip, fileno):
        print(threading.current_thread())
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            user = self.register_user(username)
        online = UserOnline(user.id, fileno)
        self.session.add(online)
        hist = LoginHistory(user.id, datetime.now(), ip)
        self.session.add(hist)

    @transaction
    def logout_user(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if user:
            self.session.query(UserOnline).filter_by(user_id=user.id).delete()

    def get_history(self):
        return self.session.query(User, LoginHistory).join(LoginHistory, User.id == LoginHistory.user_id).all()



    @transaction
    def add_contact(self, username, contactname):
        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.add_contact: user or contact not found')
            return False

        relation = Contact(user.id, contact.id)
        self.session.add(relation)

    @transaction
    def remove_contact(self, username, contactname):
        #TODO заменить на метод get_user_by_name
        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.remove_contact: user or contact not found')
            return False

        self.session.query(Contact).filter_by(user_id=user.id, contact_id=contact.id).delete()

    def get_users_online(self, *args):
        return self.session.query(User).join(UserOnline).all()

    def get_user_online(self, fd):
        return self.session.query(UserOnline).filter_by(fileno=fd).first()

    def get_contacts(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if user:
            return self.session.query(User)\
                .join(Contact, User.id == Contact.contact_id)\
                .filter(Contact.user_id == user.id)\
                .all()
                


    @transaction
    def create_room(self, roomname):
        room = RoomName(roomname)
        self.session.add(room)
        return room
    
    @transaction
    def join_user_to_room(self, room_id, user_id):
        room = Rooms(room_id, user_id)
        self.session.add(room)
        return room

    def get_room(self, roomname):
        """Возвращает чат"""
        room = self.session.query(RoomName).filter_by(name=roomname).first()
        return room

    def get_user_in_rooms(self, room_id):
        """Получаем всех юзеров из чата"""
        query = self.session.query(UserOnline, Rooms)\
            .join(Rooms, UserOnline.user_id == Rooms.user_id)\
            .filter(Rooms.room_id == room_id)\
            .all()
        return query

    def remove_user_to_room(self, room_id, user_id):
        return self.session.query(Rooms).filter_by(room_id=room_id, user_id=user_id).delete()


    @transaction
    def user_stat_update(self, username, ch_sent=0, ch_recv=0):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.user_stat_update: user not found')
            return False

        stat = self.session.query(UserStat).filter_by(user_id=user.id).first()
        if not stat:
            stat = UserStat(user.id)
            self.session.add(stat)

        stat.mes_sent += ch_sent
        stat.mes_recv += ch_recv

    def get_user_stats(self):
        return self.session.query(User, UserStat).join(UserStat, User.id == UserStat.user_id).all()



def main():
    import random
    print("Версия SQLAlchemy:", __version__)
    
    storage = ServerStorage()
    ip = '127.0.0.1'
    user1 = f'User{random.randint(0, 100)}'
    user2 = f'User{random.randint(0, 100)}'

    storage.login_user(user1, ip)
    storage.login_user(user2, ip)
    print(f'Users online: {storage.get_users_online()}')

    storage.logout_user(user1)
    print(f'Users online: {storage.get_users_online()}')



if __name__ == '__main__':
    main()