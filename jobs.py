#!/usr/bin/python3
import traceback
from datetime import date
# Define a function to create monthly contributions
def create_monthly_contributions():
    try:
        from app import storage
        from models.main_models import  MonthlyContribution

        storage.reload()
        # Get all users from the User table
        users = storage.get_all_members()
        current_date = date.today()
        date_string = current_date.strftime('%d-%m-%Y')

        contribution_no = f"CONT/{date_string}"
        contribution_amount = storage.get_setting_by_name('monthly_contribution_amount').value
        # Create a monthly contribution for each user
        
        for user in users:
            contribution_no_exists = any(monthly_cont.contribution_no == contribution_no for monthly_cont in user.monthly_contributions)
            if not contribution_no_exists:
                contribution = MonthlyContribution(
                    contribution_no=contribution_no,
                    from_user=user.id,
                    amount=contribution_amount,
                    narration="Monthly contribution",
                    is_paid=False
                )
                storage.new(contribution)
        storage.save()
        
    except Exception as e:
        # Rollback the transaction if an error occurs
        storage.rollback()
        traceback.print_exc()
    finally:
        storage.close()
