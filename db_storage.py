#!/usr/bin/python3
"""Defines the db storage methods. ie interacts with the database to create, delete, modify, query objects"""
import os
from sqlalchemy import create_engine, select, desc, and_
from sqlalchemy.orm import sessionmaker, scoped_session

from models.base_model import Base
from models.main_models import *


class DBStorage:
    """Defines a db storage object"""
    __engine = None
    __session = None
    

    def __init__(self):
        """Class constructor, instantiates a DBStorage object
        """
        MYSQL_USER = os.environ.get('MYSQL_USER', 'gerald')
        MYSQL_PWD = os.environ.get('MYSQL_PWD', 'ruphinee')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'tenum_db')

        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.format(MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB),
                pool_size=100, max_overflow=0)



    def new(self, obj):
        """Adds a new object to the current db session
        """
        self.__session.add(obj)


    def save(self):
        """Commits all changes of the current db session
        """
        self.__session.commit()

    def rollback(self):
        """Rolls back the changes in a particular session
        """
        self.__session.rollback()


    def delete(self, obj = None):
        """Deletes an object from the current db session if obj is not none
        """
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Sets a new session
        """
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False, autoflush=False)
        Session = scoped_session(sess_factory)
        self.__session = Session()

    def close(self):
        """Closes the current session
        """
        self.__session.close()

    def get_user(self, user_name):
        """Retrieves a single object of the specified class and column value
        """
        #retrieve the user with the username
        obj = self.__session.query(User).filter_by(user_name=user_name).first()
        return obj if obj else None

    def get_account_group_by_name(self, group_name):
        """Retrieve a single customer by name"""
        obj = self.__session.query(AccountGroup).filter_by(group_name=group_name).first()
        return obj if obj else None

    def get_account_by_name(self, account_name):
        """Retrieve a single account by name"""
        obj = self.__session.query(Account).filter_by(account_name=account_name).first()
        return obj if obj else None

    def get_all_objects(self, cls):
        """Retrieves all the objects of a class cls in the database
        """
        obj = self.__session.query(cls).order_by(cls.created_at.desc()).all()
        return obj if obj else None

    def get_all_paying_accounts(self):
        """Retrieve all the accounts under the account groups Cash-in-hand, Bank accounts and Mobile money(MPESA)
        """
        obj = self.__session.query(Account).filter(Account.group_name.in_(['Cash-in-hand', 'Bank account', 'Mobile money(MPESA)'])).with_entities(Account.account_name).all()
        return obj if obj else None

    def generate_document_number(self, doc_type):
        """Generates new unique document number
        """
        document_number = self.__session.query(DocumentNumber).first()

        if document_number:
            new_number = document_number.last_number
            document_number.last_number = document_number.last_number + 1
        else:
            new_number = 1
        
        self.__session.add(document_number)
        return f"{doc_type}/{new_number}"


    def get_last_payment(self, toAccount):
        """Retrieve the last payment made by the account"""
        obj = self.__session.query(Payment).filter_by(to_account=toAccount).order_by(desc(Payment.created_at)).first()
        return obj if obj else None

    def get_accounts_by_group_name(self, group_name):
        """Retrieve accounts by group_name"""
        obj = self.__session.query(Account).filter_by(group_name=group_name).all()
        return obj if obj else None

    def get_receipt_type_by_name(self, name):
        """Retrieve receipt type by name"""
        obj = self.__session.query(ReceiptType).filter_by(name=name).first()
        return obj if obj else None


    def get_all_members(self):
        """Retrieve all member users"""
        obj = self.__session.query(User).filter_by(role='member').all()
        return obj if obj else None

    def get_setting_by_name(self, name):
        """Retrieve a specific setting value"""
        obj = self.__session.query(Setting).filter_by(name=name).first()
        return obj if obj else None

    def generate_contribution_number(self, doc_type):
        """Generates new unique document number for monthly contribution
        """
        document_number = self.__session.query(DocumentNumber).first()

        if document_number:
            new_number = document_number.last_number
            document_number.last_number = document_number.last_number + 1
        else:
            new_number = 1
        self.__session.add(document_number)
        return f"{doc_type}/{new_number}"

    def get_month_cont_status(self, month, year, user_id):
        """Retrieves the payment status of the month for the particular user_id"""
        # Construct the pattern to match CONT/<month>-<year>
        pattern = f"CONT/%-{month:02d}-{year}"
        obj = self.__session.query(MonthlyContribution).filter_by(from_user=user_id).filter(MonthlyContribution.contribution_no.like(pattern)).first()
        return obj if obj else None



    def get_object_by_id(self, cls, id):
        """Retrieve a single object by id"""
        obj = self.__session.query(cls).filter_by(id=id).first()
        return obj if obj else None

    def get_unapproved_loans(self):
        """Retrieves all the unapproved loan objects of a class in the database
        """
        obj = self.__session.query(LoanRequest).filter_by(approval_status='pending').order_by(LoanRequest.created_at.desc()).all()
        return obj if obj else None


    def get_user_approval_status(self, user_id, loan_id):
        """retrieve the approval status of a user on a particular loan request"""
        obj = self.__session.query(LoanApproval).filter(LoanApproval.user_id == user_id, LoanApproval.loan_id == loan_id).first()
        return obj if obj else None


    def get_all_transactions_for_period(self, from_date, to_date):
        """retrieve all transactions for a particular period"""
        transaction_tables = [Fine, Receipt, LoanRequestTransaction, Payment]
        # Initialize an empty list to store all transactions
        all_transactions = []

        # Iterate over each transaction table
        for table in transaction_tables:
            # Query transactions within the specified date range
            transactions = self.__session.query(table).filter(and_(table.created_at >= from_date,
                                                    table.created_at <= to_date)).all()
            # Extend the list of all transactions with transactions from the current table
            all_transactions.extend(transactions)
        return all_transactions if all_transactions else None


    def get_all_accounts_excluding_loans_and_advances_accounts(self):
        """Retrieves all the accounts excluding L&A accounts
        """
        obj = self.__session.query(Account).filter(Account.group_name != "Loans and advances(Asset)").order_by(Account.created_at.desc()).all()
        return obj if obj else None

    def get_all_active_loan_numbers(self):
        """Retrieves all active loans
        """
        obj = self.__session.query(LoanRequest).filter_by(loan_status='active').order_by(LoanRequest.created_at.desc()).all()
        loan_numbers = [loan_request.loan_no for loan_request in obj]
        return loan_numbers if loan_numbers else None


