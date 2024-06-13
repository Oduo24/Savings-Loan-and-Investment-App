// Import the createSettingsForm function
const new_item_field = document.querySelector('#add_item_field');
const delete_item_from_list = document.querySelector('#receiptDetails');
const receipt_type = document.querySelector('#receipt_type');
const submit_receipt_form = document.querySelector('#receiptSaveBtn');
const outstandingBalance = document.querySelector('#getOutstandingBalance');
const newPayment = document.querySelector('#paymentSaveBtn');
const submit_fine_form = document.querySelector('#fineSaveBtn');
// const loanAmount = document.querySelector('#loanAmount');
// const loanCategory = document.querySelector('#loanCategory');
const member_approve_loan = document.querySelectorAll('button[btn_type="member_approve"]');
const disburse_loan = document.querySelectorAll('button[btn_type="admin_disburse"]');
const save_payment = document.querySelector('#paymentSaveBtn');
const settingsAnchor = document.querySelector('#settings');
const mainWrapper = document.querySelector('#main-wrapper');
const logout = document.querySelector('#logout');
const get_trial_balance_form = document.querySelector('#trialBalanceForm');
const content_body = document.querySelector('.content-body');
const get_p_and_l_form = document.querySelector('#p_and_l_form');
const add_new_account = document.querySelector('#add_new_account');
const request_for_loan = document.querySelector('#request_for_loan');

// Function that updates the sale total amount
function updateTotal() {
	let total = 0;
	document.querySelectorAll('.receipt_amount').forEach((elem) => {
	total = total + parseInt(elem.value);
	total = checkNegative(total)
	
	if (!isNaN(total)) {
		// Update the total amount
        	document.querySelector('#total_amount').innerHTML = +total;
	}
	});
}

function checkNegative(number) {
	number = parseInt(number);
	if (number < 0) {
		return number * -1;
	} else if (number === 0) {
        sweetAlert("Oops...", "Invalid zero values !!", "error");
	} else {
		return number;
	}
}

// Function that checks for empty values
function hasEmptyValue(itemsObj) {
	return Object.values(itemsObj).some(value => !value);
}

// Function that does the form submission
async function postJSON(obj, url, csrf_token=null) {
	try {
		const headers = {
			"Content-Type": "application/json"
		};

		// Add CSRF token to headers if provided
		if (csrf_token) {
			headers["X-CSRF-Token"] = csrf_token;
            headers["X-CSRFToken"] = csrf_token;
            headers["X-CSRF-TOKEN"] = csrf_token;
		}

		const response = await fetch(url, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify(obj),
			credentials: 'include' // Include cookies in the request
		});

		const result = await response.json();
        return result;
	
	} catch (error) {
		sweetAlert("Oops...", `${error} !!`, "error");
	}
}



// Validate form data for last payment form
function validateLastPaymentDetailsForm(toAccount, payingAccount) {
	if (toAccount | payingAccount === '') {
		return false;
	} else {
		return true;
	}
}

// Validate form data for payment form
function validatePaymentForm(toAccount, payingAccount, amountPaid) {
	if (toAccount | payingAccount | amountPaid === '') {
		return false;
	} else {
		return true;
	}
}


// Function to calculate and update amount to repay
function calculateAmountToRepay() {
    // Fetching user input
    let loanAmount = parseInt(document.querySelector('#loanAmount').value);
    let loanCategory = parseInt(document.querySelector('#loanCategory').value);

    // Calculate interest and total amount to repay
    let interestRate = 0.1;
    let totalInterest = loanAmount * interestRate;
    let totalRepayment = loanAmount + totalInterest;

    // Check if totalRepayment is NaN, and set it to 0 if true
    totalRepayment = isNaN(totalRepayment) ? 0 : totalRepayment;

    // Update amount to repay field
    document.querySelector('#amountToRepay').value = 'Ksh ' + totalRepayment.toFixed(2);
  }

//   Clear cookie function
  function clearCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

// Function to add content on the righr side of details section
function appendElementsToDom(elem) {
    const quixnavElement = document.querySelector('.quixnav');
    // Check if the element was found
    if (quixnavElement) {
        // Get the parent node of quixnavElement
        const parentNode = quixnavElement.parentNode;

        // Loop through each sibling element after quixnavElement and remove it
        let nextSibling = quixnavElement.nextSibling;
        while (nextSibling) {
            const siblingToRemove = nextSibling;
            nextSibling = siblingToRemove.nextSibling; // Get the next sibling before removing this one
            parentNode.removeChild(siblingToRemove); // Remove the sibling element
            }
        // Insert the sibling element after the quixnavElement
        quixnavElement.insertAdjacentElement('afterend', elem);
    }
}


function appendElementsToDom2(elem, after) {
    // Check if the 'after' element exists
    if (after && after.nextSibling) {
        // Clear all elements after the 'after' element
        let nextSibling = after.nextSibling;
        while (nextSibling) {
            const siblingToRemove = nextSibling;
            nextSibling = siblingToRemove.nextSibling;
            siblingToRemove.parentNode.removeChild(siblingToRemove);
        }
        // Insert the 'elem' after the 'after' element
        after.parentNode.insertBefore(elem, after.nextSibling);
    } else {
        // 'after' element not found or has no sibling, append 'elem' to the end
        const quixnavElement = document.querySelector('.quixnav');
        if (quixnavElement) {
            quixnavElement.parentNode.appendChild(elem);
        }
    }
}



//////////////////////// ADDING A NEW ITEM FIELD ////////////////////////
if (new_item_field) {
    new_item_field.addEventListener('click', event => {
        event.preventDefault();

        const tableBody = document.querySelector('#receiptDetails');

        // Creating a new tr element with td and form input for each row
        const tableRow = document.createElement('tr');

        // Appending 3 tableData elements to tableRow
        for (let i = 0; i < 4; i++) {
            const tableData = document.createElement('td');
            const formInput = document.createElement('input');

            // Adding class form-control to formInput
            formInput.classList.add('form-control');

            if (i == 0) {
                formInput.classList.add('from_account');
                formInput.setAttribute('list', 'fromAccounts');
            } else if (i == 1) {
                formInput.classList.add('receipt_amount');
            } else if (i == 2) {
                formInput.classList.add('remarks');
            }
            // Appending formInput to tableData
            tableData.appendChild(formInput);

            // Appending tableData to tableRow
            tableRow.appendChild(tableData);

            if (i == 3) {
                // Creating h2 Element instead of a button but in the html it is styled as a button
                // This is to prevent the default submission that occurs when Enter is pressed on an input 
                // element
                const h2Elem = document.createElement("h2");
                h2Elem.classList.add("btn");
                h2Elem.classList.add("btn-danger");
                h2Elem.classList.add("remove_receipt");
                h2Elem.innerText = "-";

                // Removing formInput element
                tableData.removeChild(formInput);
                tableRow.removeChild(tableData);

                // Appending buttonElement to the tableData element
                tableData.appendChild(h2Elem);

                // Appending tableData to tableRow
                tableRow.appendChild(tableData);
            }
        }
        tableBody.appendChild(tableRow);
    });
}


///////////////////////// REMOVING AN ITEM IN THE LIST ////////////////////////////
if (delete_item_from_list) {
    delete_item_from_list.addEventListener('click', event => {
        const target = event.target;

        if (target.classList.contains('remove_receipt')) {
            const row = target.closest('tr');
            row.remove();
            updateTotal();
        }
    });
}

if (receipt_type) {
    receipt_type.addEventListener('change', event => {
        if (receipt_type.value === 'Loan Repayment') {
            // Retrieve all pending loans
            const data = {}
            const url = '/active_loans';
            const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            // Post data to url
            postJSON(data, url, csrf_token)
            .then(result => {
                if (result.error) {
                    throw Error(result.error);
                } else if (result.invalid) {
                    swal("No data!", `${result.invalid}`, "message");
                } else {
                    // Display input group
                    active_loans_input_group = document.querySelector('#active_loans_input_group');
                    active_loans_input_group.classList.remove('d-none');
                    // Append loan number options to the dom
                    active_loans_datalist = document.querySelector('.active_loans_datalist');
                    result.forEach(loan_item => {
                        const option = document.createElement('option');
                        option.value = loan_item;
                        active_loans_datalist.appendChild(option);
                    })
                }
            })
            .catch(error => {
                sweetAlert("Oops...", `${error} !!`, "error");
            });

        }
    });
}

/////////////////////////// SUBMITTING RECEIPT FORM ////////////////////////////
if (submit_receipt_form) {
    submit_receipt_form.addEventListener('click', event => {
        event.preventDefault();

        let receipt = {};
        let individualReceipts = [];

        const paid_to_account = document.querySelector('#paid_to_account').value;
        const receipt_type = document.querySelector('#receipt_type').value;
        const receipt_date = document.querySelector('#receiptDate').value;

        
        const from_account = document.querySelectorAll('.from_account');
        const receipt_amount = document.querySelectorAll('.receipt_amount');
        const remarks = document.querySelectorAll('.remarks');


        // Iterate over receipts setting individual receipt details
        for (let index = 0; index < from_account.length; index++) {
            let receiptObj = {};

            receiptObj.from_account = from_account[index].value;
            receiptObj.receipt_amount = checkNegative(receipt_amount[index].value);
            receiptObj.remarks = remarks[index].value;


            // Check if there is any empty value
            const validity = hasEmptyValue(receiptObj);

            if (!validity) {
                individualReceipts.push(receiptObj);
            } else {
                sweetAlert("Oops...", "Empty fields !!", "error");
                return; // Stop further execution
            }
        }


        // Add individual receipt details to the receipt object
        receipt.paid_to_account = paid_to_account;
        receipt.receipt_type = receipt_type;
        if (receipt.receipt_type === 'Loan Repayment') {
            receipt.loan_number = document.querySelector('#loans_not_cleared').value;
        }

        receipt.receipt_date = receipt_date;
        receipt.individualReceipts = individualReceipts;
        
        const receiptValidity = hasEmptyValue(receipt);
        if (!receiptValidity) {
            const url = '/new_receipt';
            const csrf_token = document.querySelector('#csrf_token').value;
            // Post data to url
            postJSON(receipt, url, csrf_token)
            .then(result => {
                if (result.error) {
                    throw Error(result.error);
                } else {
                    document.querySelector('#add_new_receipt').reset();
                    swal("Success!", `${result.success}`, "success");
                }
            })
            .catch(error => {
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        } else {
            sweetAlert("Oops...", "Empty fields !!", "error");
            return; // Stop further execution
        }
    });
}


//////////////////////// LOAD LAST PAYMENT DETAILS //////////////////////////////////////
if (outstandingBalance) {
    outstandingBalance.addEventListener('click', (event) => {
    event.preventDefault();
    let toAccount = document.querySelector('#toAccount').value;
    let payingAccount = document.querySelector('#fromAccount').value;
    const url = '/last_payment_info';

    postData = {
        "toAccount": toAccount,
        "payingAccount": payingAccount
    }

    const validate1 = validateLastPaymentDetailsForm(toAccount, payingAccount);
    const csrf_token = document.querySelector('#csrf_token').value;
    
    if (validate1) {
        postJSON(postData, url, csrf_token)
        .then(result => {
            // Display to the dom
            const lastPaymentField = document.querySelector('#lastPaymentDate');
            lastPaymentField.disabled = false;
            lastPaymentField.value = result.date ? result.date : 0;
            lastPaymentField.disabled = true;

            const currentBalance = document.querySelector('#currentBalance');
            currentBalance.disabled = false;
            currentBalance.value = result.balance ? result.balance : 0;
            currentBalance.disabled = true;
        })
        .catch(error => {
            sweetAlert("Oops...", `${error} !!`, "error");
        });
    } else {
        sweetAlert("Oops...", "Empty fields !!", "error");
    }
});
}


//////////////////////////// SUBMIT NEW PAYMENT DETAILS ///////////////////////////
if (newPayment) {
    newPayment.addEventListener('click', (event) => {
        event.preventDefault();
        const toAccount = document.querySelector('#toAccount').value;
        const payingAccount = document.querySelector('#fromAccount').value;
        const amountPaid = document.querySelector('#amountPaid').value;
        const narration = document.querySelector('#payNarration').value;
        const url = '/pay';

        postData = {
            "toAccount": toAccount,
            "payingAccount": payingAccount,
            "amountPaid": amountPaid,
            "narration": narration
        }

        const validate2 = validatePaymentForm(toAccount, payingAccount, amountPaid);
        const csrf_token = document.querySelector('#csrf_token').value;

        if (validate2) {
            postJSON(postData, url, csrf_token)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                }
                swal("Success!", `${result}`, "success");
                // Clear dom content
                document.querySelector('#toAccount').value = '';
                document.querySelector('#fromAccount').value = '';
                document.querySelector('#payNarration').value = '';
                document.querySelector('#amountPaid').value = '';
                document.querySelector('#payNarration').value = '';
            })
            .catch(error => {
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        } else {
            sweetAlert("Oops...", "Empty fields !!", "error");
        }
    });
}



/////////////////////////// SUBMITTING FINE FORM ////////////////////////////
// Im using the same receipt form for fines. The names of the form fields and js variables are for receipt 
// but are translated to fine elements intuitively
if (submit_fine_form) {
    submit_fine_form.addEventListener('click', event => {
        event.preventDefault();

        let receipt = {};
        let individualReceipts = [];

        const from_account = document.querySelectorAll('.from_account');
        const receipt_amount = document.querySelectorAll('.receipt_amount');
        const remarks = document.querySelectorAll('.remarks');

        // Iterate over receipts setting individual receipt details
        for (let index = 0; index < from_account.length; index++) {
            let receiptObj = {};

            receiptObj.from_account = from_account[index].value;
            receiptObj.receipt_amount = checkNegative(receipt_amount[index].value);
            receiptObj.remarks = remarks[index].value;

            // Check if there is any empty value
            const validity = hasEmptyValue(receiptObj);

            if (!validity) {
                individualReceipts.push(receiptObj);
            } else {
                sweetAlert("Oops...", "Empty fields !!", "error");
                return; // Stop further execution
            }
        }


        // Add individual receipt details to the receipt object
        receipt.individualReceipts = individualReceipts;
        
        const receiptValidity = hasEmptyValue(receipt);
        if (!receiptValidity) {
            const url = '/new_fine';
            const csrf_token = document.querySelector('#csrf_token').value;
            // Post data to url
            postJSON(receipt, url, csrf_token)
            .then(result => {
                if (result.error) {
                    throw Error(result.error);
                } else {
                    document.querySelector('#new_fine').reset();
                    swal("Success!", `${result.success}`, "success");
                }
            })
            .catch(error => {
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        } else {
            sweetAlert("Oops...", "Missing values !!", "error");
            return; // Stop further execution
        }
    });
}

/////////////////////// Add change event listeners to loan amount and loan category fields ///////////////
if (mainWrapper) {
    mainWrapper.addEventListener('keyup', event => {
        let target = mainWrapper.querySelector('#loanAmount');
        if (event.target === target) {
            event.preventDefault();
            calculateAmountToRepay();        
        }
    })
}

if (mainWrapper) {
    mainWrapper.addEventListener('change', event => {
        let target = mainWrapper.querySelector('#loanCategory');
        if (event.target === target) {
            event.preventDefault();
            calculateAmountToRepay();        
        }
    })
}


/////////////////////// LOAN STATUS //////////////////////////
if (member_approve_loan) {
    member_approve_loan.forEach(btn => {
        btn.addEventListener('click', (ev) => {
            ev.preventDefault(); 
            loan_id = ev.target.getAttribute('loan_id');
            // Show the spinner
            const spinner = ev.target.querySelector('.spinner-border');
            spinner.classList.remove('d-none');
            
            // POST to increase count of approvals
            const url = '/loan_approval';
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            postJSON(loan_id, url, csrfToken)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                } else {
                    // remove spinner
                    spinner.classList.add('d-none');
                    ev.target.innerHTML = result;
                    ev.target.disabled=true;
                }
            })
            .catch(error => {
                spinner.classList.add('d-none');
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        })
    })
}


/////////////////////// PREVIEW DISBURSEMENT //////////////////////////
let loan_request_id = null;
if (disburse_loan) {
    disburse_loan.forEach(loan => {
        loan.addEventListener('click', (event) => {
            event.preventDefault();
            // Get loan details
            const loanee = event.target.closest('tr').querySelector('#loanee').innerText;
            const loan_amount = event.target.closest('tr').querySelector('#loan_amount').innerText;
            loan_request_id = event.target.closest('tr').querySelector('#loan_request_id').innerText;

            // Update details on loan approval modal
            const paying_to = document.querySelector('#paying_to');
            const amount_paid = document.querySelector('#amountPaid');
            const paying_from = document.querySelector('#paying_from');
            paying_to.value = loanee;
            amount_paid.value = `Ksh ${loan_amount}`;
            paying_from.value = 'Stanbic Bank';

            // Disable fields
            paying_to.disabled = true;
            amount_paid.disabled = true;
            paying_from.disabled = true;
        })
    })
}


/////////////////////// CONFIRM DISBURSEMENT //////////////////////////
if (save_payment) {
    save_payment.addEventListener('click', (event) => {
        event.preventDefault();
        
        const paying_to = document.querySelector('#paying_to').value;
        const paying_from = document.querySelector('#paying_from').value;
        const loan_amount = document.querySelector('#amountPaid').value;
        const narration = document.querySelector('#payNarration').value;

        const data = {
            paying_to,
            paying_from,
            loan_amount,
            loan_request_id,
            narration
        };
        // Begin spinner before submission
        const spinner = save_payment.querySelector('.spinner-border');
        spinner.classList.remove('d-none');

        // POST
        const url = '/loan_approval';
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        postJSON(data, url, csrfToken)
        .then(result => {
            if (result.error) {
                throw new Error(result.error);
            } else {
                // Update new state for the loan on the dom
                let disburse_btn = document.querySelector(`button[loan_id="${result.loan_id}"]`);
                disburse_btn.innerText = 'Disbursed';
                disburse_btn.disabled = true;

                let modal_close = document.querySelector('#modal_close');
                // remove spinner
                spinner.classList.add('d-none');
                modal_close.click();
                swal("Success!", `${result.success}`, "success");
            }
        })
        .catch(error => {
            // remove spinner
            spinner.classList.add('d-none');
            sweetAlert("Oops...", `${error} !!`, "error");
        });
    })
}


if (settingsAnchor) {
    // Add click event listener
    settingsAnchor.addEventListener('click', event => {
        event.preventDefault();

        // Call the function to create and append the form
        let contentBody = createSettingsForm();

        const quixnavElement = document.querySelector('.quixnav');
        // Check if the element was found
        if (quixnavElement) {
            // Get the parent node of quixnavElement
            const parentNode = quixnavElement.parentNode;

            // Loop through each sibling element after quixnavElement and remove it
            let nextSibling = quixnavElement.nextSibling;
            while (nextSibling) {
                const siblingToRemove = nextSibling;
                nextSibling = siblingToRemove.nextSibling; // Get the next sibling before removing this one
                parentNode.removeChild(siblingToRemove); // Remove the sibling element
                }
            // Insert the sibling element after the quixnavElement
            quixnavElement.insertAdjacentElement('afterend', contentBody);
        }
    });
}

if (mainWrapper) {
    mainWrapper.addEventListener('click', event => {
        let target = event.target.closest('#updateSetting');
        if (target) {
            event.preventDefault()
            const monthlyCont = document.querySelector('#monthlyCont').value;
            const lateFine = document.querySelector('#lateFine').value;
            const absentFine = document.querySelector('#absentFine').value;
            const awaFine = document.querySelector('#awaFine').value;

            const data = {
                monthly_contribution_amount: monthlyCont,
                lateFine,
                absentFine,
                awaFine
            };

            let cleaned_data = {};
            // Iterate over each key-value pair in the data object
            Object.entries(data).forEach(([key, value]) => {
                if (value) {
                    cleaned_data[key] = value;
                }
            });
            if (Object.keys(cleaned_data).length > 0) {
                // Begin spinner before submission
                const spinner = updateSetting.querySelector('#settingSpinner');
                spinner.classList.remove('d-none');

                // POST
                const url = '/settings';
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                postJSON(cleaned_data, url, csrfToken)
                .then(result => {
                    if (result.error) {  
                        throw new Error(result.error);
                    } else {
                        spinner.classList.add('d-none');
                        document.querySelector('#settingForm').reset();
                        swal("Success!", `${result.success}`, "success");
                    }
                })
                .catch(error => {
                    spinner.classList.add('d-none');
                    sweetAlert("Oops...", `${error} !!`, "error");
                });
            }
        }
    });
}

if (logout) {
    document.querySelector('#logout').addEventListener('click', (event) => {
        event.preventDefault();
        const url = '/logout';
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const data = 1;
        postJSON(data, url, csrfToken)
        .then(result => {
            if (result.error) {
                throw new Error(result.error);
            } else {
                // clearCookie('access_token_cookie');
                swal("Success!", `${result.success}`, "success");
                window.location.href = "/login"; // Redirect to login page
            }
        })
        .catch(error => {
            sweetAlert("Oops...", `${error} !!`, "error");
        });
    })
}


if (mainWrapper) {
    mainWrapper.addEventListener('click', event => {
        let target = mainWrapper.querySelector('#datePeriod');
        if (event.target === target) {
            // Begin loading spinner
            const spinner = document.querySelector('#datePeriodSpinner');
            spinner.classList.remove('d-none');

            const url = '/trial_balance';
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const from_date = document.querySelector('#fromDate').value;
            const to_date = document.querySelector('#toDate').value;
            const data = {from_date, to_date};
            postJSON(data, url, csrfToken)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                    
                } else if(result.invalid) {
                    spinner.classList.add('d-none');
                    swal(`${result.invalid} !!`);
                } else {
                    spinner.classList.add('d-none');
                    const after = document.querySelector('.content-body');

                    const accountGroups = Object.keys(result);
                    const accountBalances = result;
                    const contentBody = createAccountTable(accountGroups, accountBalances);
                    appendElementsToDom2(contentBody, after);
                }
            })
            .catch(error => {
                console.log(error);
                spinner.classList.add('d-none');
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        }
    });
}

// Display date selector for trial balance
if (get_trial_balance_form) {
    get_trial_balance_form.addEventListener('click', event => {
        event.preventDefault();
        // Create the from and to date picker
        const formDiv = createDateFields();
        appendElementsToDom(formDiv);
    });
}

// Display the date selector for income statement/P and L
if (get_p_and_l_form) {
    get_p_and_l_form.addEventListener('click', event => {
        event.preventDefault();
        // Create the from and to date picker
        const formDiv = createIncomeStatementDateSelector();
        appendElementsToDom(formDiv);
    });
}

// Set event listener to handle submission of date period for the income statement
if (mainWrapper) {
    mainWrapper.addEventListener('click', event => {
        let target = mainWrapper.querySelector('#incomeStatementDatePeriod');
        if (event.target === target) {
            // Begin loading spinner
            const spinner = document.querySelector('#datePeriodSpinner');
            spinner.classList.remove('d-none');

            const url = '/income_statement';
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const from_date = document.querySelector('#incomeStatementfromDate').value;
            const to_date = document.querySelector('#incomeStatementToDate').value;
            const data = {from_date, to_date};
            postJSON(data, url, csrfToken)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                    
                } else if(result.invalid) {
                    spinner.classList.add('d-none');
                    swal(`${result.invalid} !!`);
                } else {
                    spinner.classList.add('d-none');
                    const after = document.querySelector('.content-body');
                    const accountGroups = Object.keys(result);
                    const accountBalances = result;
                    const contentBody = createIncomeStatementTable(accountGroups, accountBalances);
                    appendElementsToDom2(contentBody, after);
                }
            })
            .catch(error => {
                console.log(error);
                spinner.classList.add('d-none');
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        }
    });
}

// EVent listener to display the add new account form
if (add_new_account) {
    add_new_account.addEventListener('click', event => {
        event.preventDefault();
        const contentBody = addNewAccountForm();
        // const after = document.querySelector('.content-body');
        appendElementsToDom(contentBody);
    })
}



// Set event listener to submit the new account details
if (mainWrapper) {
    mainWrapper.addEventListener('click', event => {
        let target = mainWrapper.querySelector('#newAccountForm');
        if (event.target === target) {
            event.preventDefault();
            // Begin loading spinner
            const spinner = document.querySelector('#newAccountSpinner');
            spinner.classList.remove('d-none');

            const url = '/add_account';
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const account_name = document.querySelector('#account_name').value;
            const account_group = document.querySelector('#account_group').value;
            const data = {account_name, account_group};
            postJSON(data, url, csrfToken)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                    
                } else {
                    spinner.classList.add('d-none');
                    swal("Success!", `${result.success}`, "success");
                    let account_form = document.querySelector('#new_account_form');
                    account_form.reset();
                }
            })
            .catch(error => {
                spinner.classList.add('d-none');
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        }
    });
}

if (request_for_loan) {
    request_for_loan.addEventListener('click', event => {
        event.preventDefault();
        const contentBody = createLoanRequestForm();
        appendElementsToDom(contentBody);
    })
}

// Set event listener to submit the loan request details
if (mainWrapper) {
    mainWrapper.addEventListener('click', event => {
        let target = mainWrapper.querySelector('#submitLoanRequest');
        if (event.target === target) {
            event.preventDefault();
            // Begin loading spinner
            const spinner = document.querySelector('#loanRequestSpinner');
            spinner.classList.remove('d-none');

            const url = '/request_loan';
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const loanAmount = document.querySelector('#loanAmount').value;
            const amountToRepay = document.querySelector('#amountToRepay').value;
            const data = {loanAmount, amountToRepay};
            postJSON(data, url, csrfToken)
            .then(result => {
                if (result.error) {
                    throw new Error(result.error);
                    
                } else if (result.invalid) {
                    console.log(result.invalid);
                    spinner.classList.add('d-none');
                    sweetAlert("Oops...!", `${result.invalid} !!`, "error");
                } else {
                    spinner.classList.add('d-none');
                    swal("Success!", `${result.success}`, "success");
                    let loan_form = document.querySelector('#loanForm');
                    loan_form.reset();
                }
            })
            .catch(error => {
                spinner.classList.add('d-none');
                sweetAlert("Oops...", `${error} !!`, "error");
            });
        }
    });
}
