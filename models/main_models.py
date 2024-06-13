#!/user/bin/python3

from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, DateTime, Date, Integer, Enum, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class DocumentNumber(Base):
    __tablename__ = 'document_numbers'

    last_number = Column(Integer, default=0, primary_key=True)


class User(BaseModel, Base):
    """Defines the User class"""
    __tablename__ = "users"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_name = Column(String(100), nullable=False)
    email_address = Column(String(100), nullable=False)
    password = Column(String(500), nullable=False)
    role = Column(Enum('admin', 'member'), nullable=False)

    # Relationships
    fines = relationship('Fine', back_populates='member')
    loan_requests = relationship('LoanRequest', back_populates='member')
    monthly_contributions = relationship('MonthlyContribution', back_populates='member')
    random_savings = relationship('RandomSaving', back_populates='member')
    receipts_from = relationship('Receipt', back_populates='member')
    payments = relationship('Payment', back_populates='member')
    loan_approvals = relationship('LoanApproval', back_populates='member')


    def __init__(self, **kwargs):
        """Initializes a User instance
        """
        super().__init__(**kwargs)


class AccountGroup(BaseModel, Base):
    """Defines the account groups class"""
    __tablename__ = 'account_groups'

    group_name = Column(String(100), nullable=False, unique=True)
    description = Column(String(250), nullable=True)
    nature_of_group = Column(Enum('asset', 'liability', 'income', 'expense', name='nature_of_account_group'), nullable=False)

    def __init__(self, **kwargs):
        """Class constructor
        """
        super().__init__(**kwargs)

# Add an index on the 'group_name' column
Index('idx_group_name', AccountGroup.group_name)



class Account(BaseModel, Base):
    """Defines the Account class"""
    __tablename__ = 'accounts'

    account_name = Column(String(100), nullable=False, unique=True)
    group_name = Column(String(100), nullable=False, unique=False)
    account_balance = Column(Float(precision=2), nullable=False, default=0)



    def __init__(self, **kwargs):
        """Class constructor
        """
        super().__init__(**kwargs)



class Receipt(BaseModel, Base):
    """Defines receipts transaction class"""
    __tablename__ = 'receipts'

    receipt_date = Column(Date)
    receipt_no = Column(String(100), nullable=False, unique=True)
    from_user = Column(String(100), ForeignKey('users.id'), nullable=False) 
    amount = Column(Float(precision=2), nullable=False)
    remark = Column(String(100), nullable=True)
    receipt_for = Column(String(100), ForeignKey('receipt_types.id'), nullable=False)
    dr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    cr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    loan_id = Column(String(100), ForeignKey('loan_requests.id'), nullable=True)

    # Relationships
    member = relationship('User', foreign_keys=[from_user], back_populates='receipts_from')
    type_of_receipt = relationship('ReceiptType', foreign_keys=[receipt_for], back_populates='receipts')
    loan = relationship('LoanRequest', foreign_keys=[loan_id], back_populates='receipts')

    def __init__(self, **kwargs):
        """Class constructor
        """
        super().__init__(**kwargs)


class ReceiptType(BaseModel, Base):
    """Defines receipts transaction class"""
    __tablename__ = 'receipt_types'

    name = Column(String(100), nullable=False, unique=True)

    # Relationships
    receipts = relationship('Receipt', back_populates='type_of_receipt')

    def __init__(self, **kwargs):
        """Class constructor
        """
        super().__init__(**kwargs)



class Payment(BaseModel, Base):
    """Defines the Payment transaction class"""
    __tablename__ = "payments"

    payment_no = Column(String(100), nullable=False, unique=True)
    to_user = Column(String(100), ForeignKey('users.id'), nullable=True)
    amount = Column(Float(precision=2), nullable=False)
    narration = Column(String(100), nullable=True)
    dr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    cr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)

    # Relationships
    member = relationship('User', foreign_keys=[to_user], back_populates='payments')

    def __init__(self, **kwargs):
        """Initializes a payment instance
        """
        super().__init__(**kwargs)



class LoanRequest(BaseModel, Base):
    """Defines a loan request class"""
    __tablename__ = "loan_requests"

    loan_no = Column(String(100), nullable=False, unique=True)
    request_from_user = Column(String(100), ForeignKey('users.id'), nullable=False)
    request_amount = Column(Float(precision=2), nullable=False)
    narration = Column(String(100), nullable=True)
    approval_status = Column(Enum('pending', 'approved', 'rejected', 'disbursed'), nullable=False, default='pending')
    issued_amount = Column(Float(precision=2), default=0)
    repayment_status = Column(Enum('normal', 'penalized'), nullable=False, default='normal')
    loan_status = Column(Enum('active', 'cleared', 'pending_approval', 'pending_disbursement'), nullable=False, default='pending_approval')
    repayment_date = Column(Date)
    repayment_amount = Column(Float(precision=2), nullable=True)
    approval_count = Column(Integer, default=0)
    outstanding_balance = Column(Float(precision=2), nullable=True)

    # Relationships
    member = relationship('User', back_populates='loan_requests')
    receipts = relationship('Receipt', back_populates='loan')

    def __init__(self, **kwargs):
        """Initializes a payloan request instance
        """
        super().__init__(**kwargs)

class LoanRequestTransaction(BaseModel, Base):
    """Defines the transaction for the loan request class"""
    __tablename__ = "loan_request_transactions"

    loan_id = Column(String(100), ForeignKey('loan_requests.id'), nullable=False)
    user_id = Column(String(100), ForeignKey('users.id'), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    dr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    cr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)

    def __init__(self, **kwargs):
        """Initializes a loan request transaction instance
        """
        super().__init__(**kwargs)


class LoanApproval(BaseModel, Base):
    """Defines the member approval class"""
    __tablename__ = "loan_approvals"

    loan_id = Column(String(100), ForeignKey('loan_requests.id'), nullable=False)
    user_id = Column(String(100), ForeignKey('users.id'), nullable=False)
    approval_status = Column(Boolean, nullable=True, default=False)

    # Relationships
    member = relationship('User', back_populates='loan_approvals')

    def __init__(self, **kwargs):
        """Initializes a loan approval instance
        """
        super().__init__(**kwargs)


class Fine(BaseModel, Base):
    """Defines a fine class"""
    __tablename__ = "fines"

    fine_no = Column(String(100), nullable=False, unique=True)
    to_user = Column(String(100), ForeignKey('users.id'), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    reason = Column(String(100), nullable=True)
    dr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    cr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)

    # Relationships
    member = relationship('User', back_populates='fines')

    def __init__(self, **kwargs):
        """Initializes a fine instance
        """
        super().__init__(**kwargs)



class MonthlyContribution(BaseModel, Base):
    """Defines a monthly contribution class"""
    __tablename__ = "monthly_contributions"

    contribution_no = Column(String(100), nullable=False)
    from_user = Column(String(100), ForeignKey('users.id'), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    narration = Column(String(100), nullable=True)
    is_paid = Column(Boolean, nullable=False, default=False)

    # Relationships
    member = relationship('User', back_populates='monthly_contributions')

    def __init__(self, **kwargs):
        """Initializes a fine instance
        """
        super().__init__(**kwargs)



class RandomSaving(BaseModel, Base):
    """Defines a random saving class"""
    __tablename__ = "random_savings"

    saving_no = Column(String(100), nullable=False, unique=True)
    from_user = Column(String(100), ForeignKey('users.id'), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    narration = Column(String(100), nullable=True)

    # Relationships
    member = relationship('User', back_populates='random_savings')

    def __init__(self, **kwargs):
        """Initializes a fine instance
        """
        super().__init__(**kwargs)

class Setting(BaseModel, Base):
    """Defines a settings class"""
    __tablename__ = "settings"

    name = Column(String(100), nullable=False, unique=True)
    value = Column(Float(precision=2), nullable=False)

    def __init__(self, **kwargs):
        """Initializes a fine instance
        """
        super().__init__(**kwargs)
 



class LoanSale(BaseModel, Base):
    """Defines the instance of transaction generated from an issued loan"""
    __tablename__ = "loan_sale_transaction"

    loan_id = Column(String(100), ForeignKey('loan_requests.id'), nullable=False)
    user_id = Column(String(100), ForeignKey('users.id'), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    dr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)
    cr_account_id = Column(String(100), ForeignKey('accounts.id'), nullable=True)

    def __init__(self, **kwargs):
        """Initializes a loan approval instance
        """
        super().__init__(**kwargs)
