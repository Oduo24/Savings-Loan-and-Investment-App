import os
import traceback
from datetime import timedelta
import datetime
import logging
from collections import defaultdict
import calendar
from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response, flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request, set_access_cookies, unset_jwt_cookies
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from jobs import create_monthly_contributions

from models.base_model import BaseModel
from models.main_models import *
from db_storage import DBStorage

from utility.number_formater import format_numbers_in_json

# Instantiate a storage object and flush all classes that needs to be mapped to database tables
storage = DBStorage()
storage.reload()
storage.save()
storage.close()


app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = 'os.urandom(32)'
app.config["JWT_SECRET_KEY"] = 'os.urandom(32)'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Instruct Flask-JWT-Extended to read tokens from cookies
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

app.config['WTF_CSRF_TIME_LIMIT'] = None # Setting this to None makes the csrf token valid for the life of the session

jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return render_template('page-login.html')


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', None)
            if user_role in roles:  # Check if user's role matches any of the required roles
                return fn(*args, **kwargs)
            else:
                return render_template('page-error-403.html'), 403
        return decorator
    return wrapper

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('page-login.html')



# INITIALIZING JOBS FOR THE APP
MYSQL_USER = os.environ.get('MYSQL_USER', 'gerald')
MYSQL_PWD = os.environ.get('MYSQL_PWD', 'ruphinee')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_DB = os.environ.get('MYSQL_DB', 'tenum_db')

# Create a SQLAlchemy job store
jobstore = {
    'default': SQLAlchemyJobStore(url="mysql+mysqldb://{}:{}@{}/{}".format(MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB))
}
# executor = {
#     'default': ThreadPoolExecutor(20),
#     'processpool': ProcessPoolExecutor(5)
# }

# Create a monthly_contribution_scheduler with the SQLAlchemy job store
monthly_contribution_scheduler = BackgroundScheduler(jobstores=jobstore)

# Add the job to the monthly_contribution_scheduler with the cron trigger
# monthly_contribution_scheduler.add_job(create_monthly_contributions, trigger='cron', day='1', month='*')
monthly_contribution_scheduler.add_job(create_monthly_contributions, trigger='cron', hour=9, minute=10, day='1', month='*')

# Start the monthly_contribution_scheduler
monthly_contribution_scheduler.start()

# monthly_contribution_scheduler.shutdown()

# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)


@app.route('/', methods=['GET'], strict_slashes=False)
def landing():
    return render_template('page-login.html')

@app.route('/index', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def admin_index():
    try:
        storage.reload()
        expense_accounts = storage.get_accounts_by_group_name('Expenses')
        income_accounts = storage.get_accounts_by_group_name('Income')
        members_equity_accounts = storage.get_accounts_by_group_name('Members equity')
        loan_accounts = storage.get_accounts_by_group_name('Loans and advances(Asset)')
        monthly_cont = storage.get_all_objects(MonthlyContribution)

        for cont in monthly_cont:
            cont.from_user = storage.get_object_by_id(User, cont.from_user).user_name


        total_expenses = sum(account.account_balance for account in expense_accounts)
        total_income = sum(account.account_balance for account in income_accounts)
        total_members_equity = sum(account.account_balance for account in members_equity_accounts)
        total_loans_issued = sum(account.account_balance for account in loan_accounts)

        paramlist = [total_expenses, total_income, total_members_equity, total_loans_issued]
        formated_paramlist = format_numbers_in_json(paramlist)

        return render_template('index.html',
                            total_expenses=formated_paramlist[0],
                            total_income=formated_paramlist[1],
                            total_members_equity=formated_paramlist[2],
                            total_loans_issued=formated_paramlist[3],
                            monthly_cont=monthly_cont
                        )
    except Exception as e:
        traceback.print_exc()
        return jsonify("Error: Backend error")
    finally:
        storage.close()

@app.route('/m_index', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('member')
def member_index():
    try:
        storage.reload()
        current_username = get_jwt_identity()
        user = storage.get_user(current_username)

        # Calculate all fines
        total_fines = sum(fine.amount for fine in user.fines)
        # Outstanding loan amount
        loan_account = storage.get_account_by_name(current_username + '_L&A')
        outstanding_loan = loan_account.account_balance

        # Calculate total savings = random savings + monthly contributions, where is_paid is true
        random_savings = sum(saving.amount for saving in user.random_savings)
        # Total monthly contributions
        total_monthly_contributions = sum(contribution.amount for contribution in user.monthly_contributions if contribution.is_paid == True)
        account_balance = storage.get_account_by_name(user.user_name).account_balance

        total_savings = random_savings + total_monthly_contributions
        # Calculate loan limit
        loan_limit = 0.75 * total_savings
        loan_limit = 0 if loan_limit <= 0 else loan_limit

        # Payment status of the current month in monthly contributions
        current_month = int(datetime.datetime.now().strftime("%m"))
        current_year = datetime.datetime.now().year
        current_monthly_cont_status = storage.get_month_cont_status(current_month, current_year, user.id)

        paramlist = [total_fines, account_balance, total_savings, loan_limit, outstanding_loan]
        formated_paramlist = format_numbers_in_json(paramlist)

        response = make_response(render_template('member_home.html',
                                username=current_username,
                                total_fines=formated_paramlist[0],
                                account_balance=formated_paramlist[1],
                                current_monthly_cont_status=current_monthly_cont_status,
                                total_savings=formated_paramlist[2],
                                loan_limit=formated_paramlist[3],
                                outstanding_loan=formated_paramlist[4]
                            ))
        return response
    except Exception as e:
        traceback.print_exc()
        return jsonify("Error: Backend error")
    finally:
        storage.close()
    


@app.route('/admin_home', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def admin_home():
    try:
        storage.reload()
        # Get the passed parameters
        username = request.args.get('username')

        expense_accounts = storage.get_accounts_by_group_name('Expenses')
        income_accounts = storage.get_accounts_by_group_name('Income')
        members_equity_accounts = storage.get_accounts_by_group_name('Members equity')
        loan_accounts = storage.get_accounts_by_group_name('Loans and advances(Asset)')
        monthly_cont = storage.get_all_objects(MonthlyContribution)

        for cont in monthly_cont:
            cont.from_user = storage.get_object_by_id(User, cont.from_user).user_name

        total_expenses = sum(account.account_balance for account in expense_accounts)
        total_income = sum(account.account_balance for account in income_accounts)
        total_members_equity = sum(account.account_balance for account in members_equity_accounts)
        total_loans_issued = sum(account.account_balance for account in loan_accounts)

        paramlist = [total_expenses, total_income, total_members_equity, total_loans_issued]
        formated_paramlist = format_numbers_in_json(paramlist)

        response = make_response(render_template('index.html',
                            total_expenses=formated_paramlist[0],
                            total_income=formated_paramlist[1],
                            total_members_equity=formated_paramlist[2],
                            total_loans_issued=formated_paramlist[3],
                            monthly_cont=monthly_cont
                        ))
        return response
    except Exception as e:
        traceback.print_exc()
        return jsonify("Error: Backend error")
    finally:
        storage.reload()

@app.route('/member_home', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('member')
def member_home():
    try:
        storage.reload()
        # Get the passed parameters
        username = request.args.get('username')

        user = storage.get_user(username)

        # Calculate all fines
        total_fines = sum(fine.amount for fine in user.fines)
        # Outstanding loan amount
        loan_account = storage.get_account_by_name(username + '_L&A')
        outstanding_loan = loan_account.account_balance

        # Calculate total savings = random savings + monthly contributions, where is_paid is true
        random_savings = sum(saving.amount for saving in user.random_savings)
        # Total monthly contributions
        total_monthly_contributions = sum(contribution.amount for contribution in user.monthly_contributions if contribution.is_paid == True)
        print(total_monthly_contributions)
        account_balance = storage.get_account_by_name(user.user_name).account_balance

        total_savings = random_savings + total_monthly_contributions
        print(total_savings)
        # Calculate loan limit
        loan_limit = 0.75 * total_savings
        loan_limit = 0 if loan_limit <= 0 else loan_limit

        # Payment status of the current month in monthly contributions
        current_month = int(datetime.datetime.now().strftime("%m"))
        current_year = datetime.datetime.now().year
        current_monthly_cont_status = storage.get_month_cont_status(current_month, current_year, user.id)

        paramlist = [total_fines, account_balance, total_savings, loan_limit, outstanding_loan]
        formated_paramlist = format_numbers_in_json(paramlist)

        response = make_response(render_template('member_home.html',
                                username=username,
                                total_fines=formated_paramlist[0],
                                account_balance=formated_paramlist[1],
                                current_monthly_cont_status=current_monthly_cont_status,
                                total_savings=formated_paramlist[2],
                                loan_limit=formated_paramlist[3],
                                outstanding_loan=formated_paramlist[4]
                            ))
        return response
    except Exception as e:
        traceback.print_exc()
        return jsonify("Error: Backend error")
    finally:
        storage.close()


@app.route('/login', methods=['POST', 'GET'], strict_slashes=False)
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        try:
            storage.reload()
            user = storage.get_user(username)

            if not user or not check_password_hash(user.password, password):
                flash('Login failed. Please check your username and password.', 'danger')
                return redirect(url_for('login'))
            
            if user.role == 'admin':
                response = make_response(redirect(url_for('admin_home', username=user.user_name,)))
                access_token = create_access_token(identity=username, additional_claims={"role": user.role}, expires_delta=timedelta(hours=24))
                set_access_cookies(response, access_token)
                return response
            else:
                response = make_response(redirect(url_for('member_home', username=user.user_name,)))
                access_token = create_access_token(identity=username, additional_claims={"role": user.role}, expires_delta=timedelta(hours=24))
                set_access_cookies(response, access_token)
                return response
        except Exception as e:
            traceback.print_exc()
        finally:
            storage.close()
    else:
        return render_template('page-login.html')



@app.route('/register', methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def register_user():
    if request.method == 'POST':
        storage.reload()
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_name = request.form.get('user_name')
        email_address = request.form.get('email_address')
        password = request.form.get('password')
        role = request.form.get('role')

        # Early return if essential fields are missing
        if not all([first_name, last_name, user_name, email_address, password, role]):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if user_name already exists
            if storage.get_user(username):
                return jsonify({"error": "Username already exists"}), 400

        password_hashed = generate_password_hash(password)

        try:
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                user_name=user_name,
                email_address=email_address,
                password=password_hashed,
                role=role
            )
            storage.new(new_user)

            # Add an account for the user if user is not admin user
            if role == 'member':
                new_account = Account(
                    account_name=new_user.user_name,
                    group_name='Members equity',
                    account_balance=0
                )

                new_loan_and_advances_account = Account(
                    account_name=user_name + '_L&A',
                    group_name='Loans and advances(Asset)',
                    account_balance=0
                )

                storage.new(new_account)
                storage.new(new_loan_and_advances_account)

                # Add monthly contribution status for the current month for the user
                create_new_monthly_contribution(new_user.id)

                storage.save()
                return redirect(url_for('register_user'))
            else:
                storage.save()
                return redirect(url_for('register_user'))

        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
        finally:
            storage.close()
    else:
        return render_template('page-register.html')


# Define a function to create new monthly contribution status
def create_new_monthly_contribution(user_id):
    current_date = datetime.date.today()
    date_string = current_date.strftime('%d-%m-%Y')

    contribution_no = f"CONT/{date_string}"
    contribution_amount = storage.get_setting_by_name('monthly_contribution_amount').value
    # Create a monthly contribution for the user
    contribution = MonthlyContribution(
        contribution_no=contribution_no,
        from_user=user_id,
        amount=contribution_amount,
        narration="Monthly contribution",
        is_paid=False
    )
    storage.new(contribution)
        

@app.route('/add_account', methods=['POST',], strict_slashes=False)
@jwt_required()
@role_required('admin')
def new_account():
    """Adds a new account to the database
    """
    claims = get_jwt()
    if request.method == 'POST':
        try:
            storage.reload()
            form_details = request.get_json()
            account_name = form_details['account_name']
            group_name = form_details['account_group']

            # Check if account exists
            if storage.get_account_by_name(account_name):
                return jsonify({"error": "Account name already exists in the system"})


            # Creating the Account object
            account_object = Account(
                account_name=account_name,
                group_name=group_name
            )

            # Saving the account to the database
            storage.new(account_object)
            storage.save()
            return jsonify({"success": f"New Account {account_object.account_name} created."})
        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": "Unknown Exception occured"})
        finally:
            storage.close()
    # else:
    #     return render_template('add-account.html')

        
@app.route('/new_receipt', methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def receive_payment():
    if request.method == 'POST':
        try:
            
            storage.reload()
            receipt_details = request.get_json()

            # Dr account involved
            paid_to_account = storage.get_account_by_name(receipt_details["paid_to_account"])
            receipt_for = storage.get_receipt_type_by_name(receipt_details["receipt_type"])

            generated_receipts = []
            for individual_receipt in receipt_details["individualReceipts"]:
                receipt_no = storage.generate_document_number("RCT")
                generated_receipts.append(receipt_no)
                # Cr account involved
                from_account = storage.get_account_by_name(individual_receipt["from_account"])

                # User
                from_user = storage.get_user(from_account.account_name)
                if not from_user:
                    return jsonify({"error":  "Wrong LEDGER NAME selected"}), 500

                # Handling receipt date
                date_format = "%Y-%m-%d"
                # Parse the string into a datetime object
                parsed_date = datetime.datetime.strptime(receipt_details["receipt_date"], date_format).date()

                # Handle receipt types
                if receipt_for.name == 'Monthly Contribution':
                    # Check that the user at least selected the correct LEDGER NAME with account group being equity
                    if from_account.group_name != 'Members equity':
                        storage.rollback()
                        return jsonify({"error":  "Wrong LEDGER NAME selected"}), 500
                    month = parsed_date.month
                    year = parsed_date.year
                    # Check the payment status of the month in monthly contributions
                    monthly_cont_status = storage.get_month_cont_status(month, year, from_user.id)
                    if monthly_cont_status.is_paid == True:
                        return jsonify({"error": f"Monthly contribution for month {month} for member {from_user.user_name} already paid. You may want to consider taking it as a saving."}), 500
                    else:
                        receiptObj = {
                        "receipt_date": parsed_date,
                        "receipt_no": receipt_no,
                        "amount": individual_receipt["receipt_amount"],
                        "remark": individual_receipt["remarks"],
                        "from_user": from_user.id,
                        "receipt_for": receipt_for.id,
                        "dr_account_id": paid_to_account.id,
                        "cr_account_id": from_account.id
                        }
                        new_receipt = Receipt(**receiptObj)
                        storage.new(new_receipt)

                        # Set is_paid to True
                        monthly_cont_status.is_paid = True
                        storage.new(monthly_cont_status)

                        # Update account balance
                        from_account.account_balance -= int(individual_receipt["receipt_amount"])
                        storage.new(from_account)

                elif receipt_for.name == 'Savings':
                    # Check that the user at least selected the correct LEDGER NAME with account group being equity
                    if from_account.group_name != 'Members equity':
                        storage.rollback()
                        return jsonify({"error":  "Wrong LEDGER NAME selected"}), 500

                    receiptObj = {
                    "receipt_date": parsed_date,
                    "receipt_no": receipt_no,
                    "amount": individual_receipt["receipt_amount"],
                    "remark": individual_receipt["remarks"],
                    "from_user": from_user.id,
                    "receipt_for": receipt_for.id,
                    "dr_account_id": paid_to_account.id,
                    "cr_account_id": from_account.id
                    }
                    new_receipt = Receipt(**receiptObj)
                    storage.new(new_receipt)

                    # Update account balance
                    from_account.account_balance -= int(individual_receipt["receipt_amount"])
                    storage.new(from_account)

                    # Create a random savings object
                    saving_obj = RandomSaving(
                        saving_no=storage.generate_document_number('SAV'),
                        from_user=from_user.id,
                        amount=individual_receipt["receipt_amount"],
                    )
                    storage.new(saving_obj)
                elif receipt_for.name == 'Loan Repayment':
                    loan_number = receipt_details["loan_number"]
                    # Credit member loan account
                    member_loan_account = storage.get_account_by_name(from_user.user_name + "_L&A")
                    if not member_loan_account:
                        storage.rollback()
                        return jsonify({"error": "Wrong LEDGER NAME selected"}), 500
                    receiptObj = {
                    "receipt_date": parsed_date,
                    "receipt_no": receipt_no,
                    "amount": individual_receipt["receipt_amount"],
                    "remark": individual_receipt["remarks"],
                    "from_user": from_user.id,
                    "receipt_for": receipt_for.id,
                    "dr_account_id": paid_to_account.id,
                    "cr_account_id": member_loan_account.id
                    }
                    new_receipt = Receipt(**receiptObj)
                    storage.new(new_receipt)

                    # Updating account balance
                    member_loan_account.account_balance -= new_receipt.amount
                    storage.new(member_loan_account)

                    # Decrease the outstanding balance of the loan
                    for loan in from_user.loan_requests:
                        if loan.loan_no == loan_number:
                            loan.outstanding_balance -= new_receipt.amount
                            storage.new(loan)
                            break

                # Updating account balance
                paid_to_account.account_balance += int(individual_receipt["receipt_amount"])
                storage.new(paid_to_account)
            storage.save()

                # Call a function that sends notification to member that his account has been credited

            return jsonify({"success": f"New receipt number created: {generated_receipts}"}), 200

        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": "Error saving receipt information"}), 500
        finally:
            storage.close()

    else:
        from_accounts = storage.get_all_accounts_excluding_loans_and_advances_accounts()
        to_accounts = storage.get_all_paying_accounts()
        receipt_types = storage.get_all_objects(ReceiptType)
        return render_template(
            'receipt.html',
            from_accounts=from_accounts, 
            to_accounts=to_accounts,
            receipt_types=receipt_types
        )


@app.route("/active_loans", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required('admin')
def retrieve_active_loans():
    if request.method == 'POST':
        try:
            # Retrieve all active loans
            active_loans = storage.get_all_active_loan_numbers()
            if active_loans:
                return active_loans
            return jsonify({"invalid":"No active loans present"})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": "Retrieving pending loans"})
        finally:
            storage.close()

@app.route('/pay', methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def payment():
    if request.method == 'POST':
        try:
            storage.reload()
            payment_details = request.get_json()
            payment_no = storage.generate_document_number("PAY")
            # Handle the transaction.
            paying_account = storage.get_account_by_name(payment_details["payingAccount"])
            toAccount = storage.get_account_by_name(payment_details["toAccount"])

            to_user = storage.get_user(payment_details["toAccount"])
            payment = {
                        "to_user": to_user.id if to_user else None,
                        "payment_no": payment_no,
                        "amount": payment_details["amountPaid"],
                        "narration": payment_details["narration"],
                        "dr_account_id": toAccount.id,
                        "cr_account_id": paying_account.id,
                    }
            
            new_payment = Payment(**payment)

            storage.new(new_payment)

            # update the account balances
            toAccount.account_balance = toAccount.account_balance + int(payment_details["amountPaid"])
            paying_account.account_balance = paying_account.account_balance - int(payment_details["amountPaid"])
            storage.new(paying_account)
            storage.new(toAccount)

            return jsonify(f"SUCCESS. \n Payment number {payment_no} created."), 200  
        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": f"Could not create a new payment. \n {e}"}), 500
        finally:
            storage.save()
            storage.close()
    else:
        accounts = storage.get_all_accounts_excluding_loans_and_advances_accounts()
        paying_accounts = storage.get_all_paying_accounts()

        return render_template('payment.html',
                            accounts=accounts,
                            paying_accounts=paying_accounts
                            )

@app.route('/last_payment_info', methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def last_payment_info():
    """Get the details of last payment made"""
    if request.method == 'POST':
        try:
            toAccount_and_payingAccount = request.get_json()

            # Get last payment
            storage.reload()
            last_payment = storage.get_last_payment(toAccount_and_payingAccount["toAccount"])
            balance = storage.get_account_by_name(toAccount_and_payingAccount["toAccount"]).account_balance

            if last_payment:
                # Return last payment details
                last_payment_details = {
                    "date": last_payment.created_at.strftime("%d/%m/%Y"),
                    "balance": balance
                }
                result = jsonify(last_payment_details)
                return result, 200
            else:
                last_payment_details = {
                        "date": 0,
                        "balance": 0
                }
                result = jsonify(last_payment_details)
                return result, 200

        except Exception as e:
            return jsonify({"error": f"Could not retrieve last payment information {e}"})
        finally:
            storage.close()



@app.route('/new_fine', methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
@role_required('admin')
def fine():
    if request.method == 'POST':
        try:
            storage.reload()
            receipt_details = request.get_json()

            # Cr account involved
            paid_to_account = storage.get_account_by_name("Fines")

            generated_fines = []
            for individual_receipt in receipt_details["individualReceipts"]:
                receipt_no = storage.generate_document_number("FIN")
                generated_fines.append(receipt_no)
                # Dr account involved
                from_account = storage.get_account_by_name(individual_receipt["from_account"])
                
                fineObj = {
                    "fine_no": receipt_no,
                    "amount": individual_receipt["receipt_amount"],
                    "reason": individual_receipt["remarks"],
                    "to_user": storage.get_user(from_account.account_name).id,
                    "dr_account_id": from_account.id,
                    "cr_account_id": paid_to_account.id
                }
                new_fine = Fine(**fineObj)
                storage.new(new_fine)

                # Updating account balances
                from_account.account_balance += int(individual_receipt["receipt_amount"])
                paid_to_account.account_balance -= int(individual_receipt["receipt_amount"])
                storage.new(paid_to_account)
                storage.new(from_account)

                # Call a function that sends notification to member that his account has been debited(Fined)

            return jsonify({"success": f"New fine created: {generated_fines}"}), 200

        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": "Error saving fine information"}), 500
        finally:
            storage.save()
            storage.close()

    else:
        from_accounts = storage.get_all_objects(Account)
        return render_template('fine.html', from_accounts=from_accounts)



@app.route('/member_payments', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('member')
def get_member_payments():
    if request.method == 'GET':
        try:
            storage.reload()
            if request.method == 'GET':
                current_username = get_jwt_identity()
                user = storage.get_user(current_username)

                for receipt in user.receipts_from:
                    receipt_type = storage.get_object_by_id(ReceiptType, receipt.receipt_for).name
                    account_name = storage.get_object_by_id(Account, receipt.dr_account_id).account_name

                    receipt.receipt_for = receipt_type
                    receipt.dr_account_id = account_name

                return render_template('member_payments.html', 
                                        current_username=current_username,
                                        payments=user.receipts_from   # Payments are receipts on the backend admin view
                                    )
        except Exception as e:
            traceback.print_exc()
        finally:
            storage.close()


@app.route('/request_loan', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
@role_required('member')
def request_loan():
    try:
        storage.reload()
        current_username = get_jwt_identity()
        user = storage.get_user(current_username)
        user_account = storage.get_account_by_name(user.user_name)
        
        # account_balance = user_account.account_balance
        
        # Calculate total savings = random savings + monthly contributions, where is_paid is true
        random_savings = sum(saving.amount for saving in user.random_savings)
        # Total monthly contributions
        total_monthly_contributions = sum(contribution.amount for contribution in user.monthly_contributions if contribution.is_paid == True)
        total_savings = random_savings + total_monthly_contributions
        # Total active loans(Principal Amount)
        total_outstanding_loan_balance = 0
        for loan in user.loan_requests:
            if loan.loan_status == 'active':
                total_outstanding_loan_balance += float(loan.outstanding_balance)

        # Account balance is equal to total savings minus active loans(Principal Amount)
        account_balance = total_savings - total_outstanding_loan_balance

        # Calculate loan limit(75% of member's equity) minus outstanding loans
        member_equity = user_account.account_balance
        loan_limit = 0.75 * abs(member_equity) - total_outstanding_loan_balance
        loan_limit = 0 if loan_limit < 0 else loan_limit

        if request.method == 'POST':
            loan_data = request.get_json()
            loan_amount = int(loan_data['loanAmount']) 
            

            # Early return if there is a pending request not yet approved
            for loan_request in user.loan_requests:
                if loan_request.approval_status == "pending":
                    return jsonify(invalid="You have a pending loan request which has not been approved..."), 200

            # Early return if loan amount exceeds loan limit
            if loan_amount > loan_limit:
                return jsonify({"invalid": "I can't let you do that! You do not qualify for the requested amount. Please continue saving to qualify for more loans."})

            loan_no = storage.generate_document_number('LN')
            current_date = datetime.datetime.now().date()
            repayment_amount = 1.1 * loan_amount
            if loan_amount < 30000:
                # Add 2 months to the current date
                repayment_date = current_date + timedelta(days=2*30)
            else:
                 # Add 4 months to the current date
                repayment_date = current_date + timedelta(days=4*30)

            new_loan_request=LoanRequest(
                loan_no=loan_no,
                request_from_user=user.id,
                request_amount=loan_amount,
                repayment_date=repayment_date,
                repayment_amount=repayment_amount,
                outstanding_balance=0.00
            )
            storage.new(new_loan_request)
            storage.save()
            # Create a loan approval log to track users approvals and number of approvals
            new_loan_approval_status = LoanApproval(
                loan_id=new_loan_request.id,
                user_id=user.id
            )
            storage.new(new_loan_approval_status)
            

            # # debiting and crediting appropriate accounts
            # user_loan_account_balance = storage.get_account_by_name(user.user_name + "_L&A")
            # loan_revenue_Account = storage.get_account_by_name("Loan Revenue")
            # new_loan_sale = LoanSale(
            #     loan_id=new_loan_request.id,
            #     user_id=user.id,
            #     amount=new_loan_request.repayment_amount,
            #     dr_account_id=user_loan_account_balance.id
            #     cr_account_id=loan_revenue_Account.id
            # )
            # storage.new(new_loan_sale)

            # # Updating account balances
            # user_loan_account_balance += float(new_loan_request.repayment_amount)
            # loan_revenue_Account -= float(new_loan_request.repayment_amount)

            storage.save()
            return redirect(url_for('approve_loan'))
        else:
            paramlist = [account_balance, loan_limit]
            formated_paramlist = format_numbers_in_json(paramlist)
            return render_template('request_loan.html', 
                                    username=current_username,
                                    account_balance=formated_paramlist[0],
                                    loan_limit=formated_paramlist[1]
                                )
    except Exception as e:
        storage.rollback()
        traceback.print_exc()
        return jsonify({"error": "Could not create a loan request"})
    finally:
        # storage.save()
        storage.close()


@app.route('/loan_approval', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
@role_required('member', 'admin')
def approve_loan():
    claims = get_jwt()
    role = claims.get('role', None)
    current_username = get_jwt_identity()
    try:
        storage.reload()
        user = storage.get_user(current_username)
        loan_requests = storage.get_unapproved_loans()
        
        if role == 'member':
            loan_id = None
            if request.method == 'POST':
                try:
                    storage.reload()
                    loan_id = request.get_json()
                    user_approval = storage.get_user_approval_status(user.id, loan_id)
                    user_approval_status = user_approval.approval_status if user_approval else None
                    #  Update loan approval count
                    loan_request = storage.get_object_by_id(LoanRequest, loan_id)
                    loan_request.approval_count += 1

                    if loan_request.approval_count >= 3:
                        loan_request.approval_status = 'approved'
                        loan_request.loan_status = 'pending_disbursement'
                    # Approval status log
                    approval_status_update = LoanApproval(
                        loan_id=loan_request.id,
                        user_id=user.id,
                        approval_status=1
                    )
                    storage.new(approval_status_update)
                    storage.save()
                    return jsonify("Approved"), 200
                except Exception as e:
                    storage.rollback()
                    traceback.print_exc()
                    return jsonify({"error": "backend error"})
                finally:
                    storage.close()
            else:
                if not loan_requests:
                    return render_template('loan_requests.html', current_username=current_username)
                       
                for loan_request in loan_requests:
                    loan_request.request_from_user = storage.get_object_by_id(User, loan_request.request_from_user).user_name
                
                ids_of_approved_loans = [approval.loan_id for approval in user.loan_approvals]
                
                return render_template(
                    'loan_requests.html',
                    current_username=current_username,
                    loan_requests=loan_requests,
                    role=role,
                    user_approvals=ids_of_approved_loans
                )
        else:
            if request.method == 'POST':
                try:
                    storage.reload()
                    loan_details = request.get_json()
                    repayment_amount = float(loan_details["loan_amount"].split()[1]) * 1.1
                    # Change status of loan to disbursed
                    loan_obj = storage.get_object_by_id(LoanRequest, loan_details["loan_request_id"])
                    #  Accounts involved
                    paying_from_account = storage.get_account_by_name(loan_details["paying_from"])
                    member_loan_account = storage.get_account_by_name(loan_details["paying_to"] + "_L&A")

                    loan_obj.approval_status = 'disbursed'
                    loan_obj.loan_status = 'active'
                    loan_obj.repayment_amount = repayment_amount
                    loan_obj.narration = loan_details["narration"]

                    storage.new(loan_obj)


                    # Credit paying_from_account and debit member_loan_account
                    paying_from_account.account_balance -= loan_obj.request_amount
                    member_loan_account.account_balance += repayment_amount
                    storage.new(paying_from_account)
                    storage.new(member_loan_account)

                    # Create a transaction object for the LoanRequestTransaction
                    new_loan_transaction_obj = LoanRequestTransaction(
                        loan_id=loan_obj.id,
                        amount=repayment_amount,
                        user_id=loan_obj.request_from_user,
                        dr_account_id=member_loan_account.id,
                        cr_account_id=paying_from_account.id
                    )
                    storage.new(new_loan_transaction_obj)

                    storage.save()
                    return jsonify({"success": "Loan Disbursed", "loan_id": f"{loan_obj.id}"})

                except Exception as e:
                    storage.rollback()
                    traceback.print_exc()
                    return jsonify({"error": "Could not disburse loan"})
                finally:
                    storage.close()
            else:
                loan_requests = storage.get_all_objects(LoanRequest)
                if not loan_requests:
                    return render_template('admin_loan_requests.html', current_username=current_username)

                for loan_request in loan_requests:
                    loan_request.request_from_user = storage.get_object_by_id(User, loan_request.request_from_user).user_name
                return render_template(
                    'admin_loan_requests.html',
                    current_username=current_username,
                    loan_requests=loan_requests,
                    role=role
                )
    except Exception as e:
        storage.rollback()
        traceback.print_exc()
        return jsonify({"error": "backend error"})
    finally:
        storage.close()


@app.route('/my_loans', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('member')
def my_loans():
    if request.method == 'GET':
        try:
            storage.reload()
            current_username = get_jwt_identity()
            user = storage.get_user(current_username)

            for loan in user.loan_requests:
                loan.request_from_user = storage.get_object_by_id(User, loan.request_from_user).user_name

            return render_template('member_loans.html',
                                    current_username=current_username,
                                    loans=user.loan_requests
                                )
        except Exception as e:
            traceback.print_exc()
        finally:
            storage.close()


@app.route('/fines', methods=['GET'], strict_slashes=False)
@jwt_required()
@role_required('member')
def my_fines():
    if request.method == 'GET':
        try:
            storage.reload()
            current_username = get_jwt_identity()
            user = storage.get_user(current_username)

            return render_template('member_fines.html',
                                    current_username=current_username,
                                    fines=user.fines
                                )
        except Exception as e:
            traceback.print_exc()
        finally:
            storage.close()


@app.route('/settings', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
@role_required('member', 'admin')
def settings():
    claims = get_jwt()
    role = claims.get('role', None)
    current_username = get_jwt_identity()
    if request.method == 'POST':
        setting_data = request.get_json()

        storage.reload()
        try:
            if role == 'admin':   
                for setting_name, new_value in setting_data.items():
                    setting = storage.get_setting_by_name(setting_name)
                    setting.value = new_value
                    storage.new(setting)
                storage.save()
                return jsonify({"success": "Settings updated successfuly"})
            else:
                pass
        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": "Error updating settings"})
        finally:
            storage.close()
               

@app.route('/member_savings_data', methods=['GET', 'POST'], strict_slashes=False)
@jwt_required()
@role_required('member', 'admin')
def member_savings_data():
    claims = get_jwt()
    role = claims.get('role', None)
    current_username = get_jwt_identity()
    if request.method == 'POST':
        storage.reload()
        try:
            if role == 'member':   
                user = storage.get_user(current_username)
                # Initialize dictionaries to store amounts and months
                totals_by_month = defaultdict(list)
                # Iterate over monthly contributions
                for contribution in user.monthly_contributions:
                    if contribution.is_paid == True:
                        month_name = contribution.created_at.strftime('%B')  # Get the full month name
                        amount = contribution.amount
                        totals_by_month[month_name].append(amount)

                # Iterate over random savings
                for saving in user.random_savings:
                    month_name = saving.created_at.strftime('%B')  # Get the full month name
                    amount = saving.amount
                    totals_by_month[month_name].append(amount)

                # Calculate the total amounts for each month
                totals = {month: sum(amounts) for month, amounts in totals_by_month.items()}
                totals_by_month_integer = {list(calendar.month_name).index(month): amount for month, amount in totals.items()}
                # Include missing months in between with an amount of zero
                max_index = max(totals_by_month_integer.keys())
                min_index = min(totals_by_month_integer.keys())
                min_index = min_index if min_index != max_index else 1
                for i in range(min_index, max_index):
                    if i not in totals_by_month_integer.keys():
                        totals_by_month_integer[i] = 0
                
                # Sort based on index
                sorted_totals = dict(sorted(totals_by_month_integer.items()))

                totals_with_month_names = {}
                for month, amount in sorted_totals.items():
                    totals_with_month_names[calendar.month_name[month]] = amount

                # Extract the sorted months and amounts
                months = [month for month, _ in totals_with_month_names.items()]
                amounts = [amount for _, amount in totals_with_month_names.items()]
                return jsonify(month=months, amount=amounts)
            else:
                usernames = []
                total_member_savings = []
                users = storage.get_all_objects(User)
                for user in users:
                    if user.role == 'member':
                        total_amount = 0
                        usernames.append(user.user_name)
                        # Calculate total contributions and savings
                        for contribution in user.monthly_contributions:
                            if contribution.is_paid == True:
                                total_amount += contribution.amount
                        
                        for saving in user.random_savings:
                            total_amount += saving.amount
                        total_member_savings.append(total_amount)
                        # return usernames as month to be able to use the same graph on the client side
                return jsonify(month=usernames, amount=total_member_savings)
        except Exception as e:
            storage.rollback()
            traceback.print_exc()
            return jsonify({"error": "Error Retrieving savings history"})
        finally:
            storage.close()

    else:
        return redirect(url_for('login'))


@app.route("/logout", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required('member', 'admin')
def logout():
    try:
        # Calculate the expiry date as a past date
        expiry_date = datetime.datetime.utcnow() - timedelta(days=1)
        # Convert expiry_date to a string in the required format
        expiry_str = expiry_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Clear JWT cookies to invalidate the token
        response = jsonify({"success": "Logout successful"})

        # Set the access_token cookie to expire in the past
        response.set_cookie('access_token_cookie', '', expires=expiry_str)
        return response

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error logging out"})


# Define the unauthorized loader function
@jwt.unauthorized_loader
def unauthorized_callback(reason):
    # Redirect the user to the login page or handle the response accordingly
    # response = jsonify({'message': 'Unauthorized: ' + reason})
    # response.status_code = 401  # Unauthorized
    return redirect(url_for('login'))



@app.route("/trial_balance", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required('admin')
def create_trial_balance():
    if request.method == 'POST':
        try:
            storage.reload()
            period = request.get_json()
            # Handling receipt date
            date_format = "%Y-%m-%d"
            # Parse the string into a datetime object
            from_date = datetime.datetime.strptime(period["from_date"], date_format).date()
            to_date = datetime.datetime.strptime(period["to_date"], date_format).date()
            # Query all transactions in the selected period from all transaction tables
            transactions = storage.get_all_transactions_for_period(from_date, to_date)

            if not transactions:
                return jsonify({"invalid": "No transactions for the selected period"})

            # Initialize a dictionary to store account balances
            all_accounts = storage.get_all_objects(Account)
            account_balances = {account.id: 0 for account in all_accounts}

            # Update account balances based on transactions
            for transaction in transactions:
                account_balances[transaction.cr_account_id] -= transaction.amount
                account_balances[transaction.dr_account_id] += transaction.amount
            
            # Define dictionaries to store balances for each category
            assets_balances = {}
            liabilities_balances = {}
            equity_balances = {}
            revenue_balances = {}
            expenses_balances = {}
            dividend_balances = {}

            # Iterate over account balances with IDs
            for account_id, balance in account_balances.items():
                # Find the corresponding account object
                account = next((acc for acc in all_accounts if acc.id == account_id), None)
                if account:
                    # Append account name and balance to the appropriate category dictionary
                    if account.group_name in ['Loans and advances(Asset)', 'Cash-in-hand', 'Bank account', 'Mobile money(MPESA)', 'Fixed assets', 'Current assets']:
                        assets_balances[account.account_name] = balance
                    elif account.group_name == 'Members equity':
                        equity_balances[account.account_name] = balance
                    elif account.group_name == 'Income':
                        revenue_balances[account.account_name] = balance
                    elif account.group_name in ['Expenses',]:
                        expenses_balances[account.account_name] = balance
                    elif account.group_name in ['Duties and taxes', 'Liability', 'Loan(Liability)']:
                        liabilities_balances[account.account_name] = balance
                    elif account.group_name in ['Dividends',]:
                        dividend_balances[account.account_name] = balance

            return jsonify(
                Assets=assets_balances if assets_balances else {"zero accounts": "0"},
                Liabilities=liabilities_balances if liabilities_balances else {"zero accounts": "0"},
                Equity=equity_balances if equity_balances else {"zero accounts": "0"},
                Revenue=revenue_balances if revenue_balances else {"zero accounts": "0"},
                Expenses=expenses_balances if expenses_balances else {"zero accounts": "0"},
                Dividends = dividend_balances if dividend_balances else {"zero accounts": "0"}
            )
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": "Error generating trial balance"})

        finally:
            storage.close()


@app.route("/income_statement", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required('admin')
def create_income_statement():
    if request.method == 'POST':
        try:
            storage.reload()
            period = request.get_json()
            # Handling receipt date
            date_format = "%Y-%m-%d"
            # Parse the string into a datetime object
            from_date = datetime.datetime.strptime(period["from_date"], date_format).date()
            to_date = datetime.datetime.strptime(period["to_date"], date_format).date()

            # Obtain revenue and expense accounts
            revenue_accounts = storage.get_accounts_by_group_name('Income')
            expense_accounts = storage.get_accounts_by_group_name('Expenses')

            # Query all transactions in the selected period
            # These transactions should be only those that involve revenue and expense accounts
            # Calculate the balances of these accounts for the period from the transactions
            transactions = storage.get_all_transactions_for_period(from_date, to_date)

            # Initialize revenue and expense accounts balances
            revenue_account_balances = {account.id: 0 for account in revenue_accounts}
            expense_account_balances = {account.id: 0 for account in expense_accounts}
            

            if not transactions:
                return jsonify({"invalid": "No transactions for the selected period"})

            # Calculate the balances using the transactions for that period
            for transaction in transactions:
                # the dr_account_id column contains the account that was debited for the transaction
                # and the cr_account_id contains the id of the account that was credited for the transaction.
                # So for the revenue account where the id is 'cr_account_id' means that account was credited.
                # when you credit a revenue account it means it increased(Normal credit account). So we calculate
                # balances using -ve for crediting and +ve for debiting.

                # First check if the cr_account_id indeed belongs to a revenue account
                rev_account = next((acc for acc in revenue_accounts if acc.id == transaction.cr_account_id), None)
                if rev_account:
                    revenue_account_balances[transaction.cr_account_id] -= transaction.amount

                # First check if the dr_account_id indeed belongs to an expense account
                exp_account = next((acc for acc in expense_accounts if acc.id == transaction.dr_account_id), None)
                if exp_account:
                    expense_account_balances[transaction.dr_account_id] += transaction.amount

            # Create a new dictionary to store revenue account names with balances
            revenue_account_balances_with_names = {}
            # Create a new dictionary to store expense account names with balances
            expense_account_balances_with_names = {}

            # Replace revenue account ids with account names in the balances
            for account_id, balance in revenue_account_balances.items():
                # Find the corresponding account object
                account = next((acc for acc in revenue_accounts if acc.id == account_id), None)
                if account:
                    # Assign the account name as the key and balance as the value in the new dictionary
                    revenue_account_balances_with_names[account.account_name] = balance

            # Replace expense account ids with account names in the balances
            for account_id, balance in expense_account_balances.items():
                # Finding corresponding account object
                account = next((acc for acc in expense_accounts if acc.id == account_id), None)
                if account:
                   expense_account_balances_with_names[account.account_name] = balance
            return jsonify(
                Expenses=expense_account_balances_with_names if expense_account_balances_with_names else {"zero accounts": "0"},
                Revenues=revenue_account_balances_with_names if revenue_account_balances_with_names else {"zero accounts": "0"}  
            )
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": "Error generating P&L"})
        finally:
            storage.close()


@app.route("/balance_sheet", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required('admin')
def create_balance_sheet():
    if request.method == 'POST':
        try:
            pass
            # Determine income/Close temporary accounts/Prepare income summary/Prepare P&L
            # expense_and_revenue_accounts = create_income_statement()

            # Get assets, liabilities and equity accounts

            # Return assets, liabilities and equity accounts together with the Income(Profit/Loss)

        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": "Error generating P&L"})
        finally:
            storage.close()




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    # try:
    #     app.run(host="0.0.0.0", port=5003, debug=True)
    # except (KeyboardInterrupt, SystemExit):
    #     pass
    # finally:
    #     # Shut down the scheduler when exiting the app
    #     # scheduler.shutdown()
    #     pass

    
