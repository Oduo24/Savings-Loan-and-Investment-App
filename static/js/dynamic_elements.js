function createWelcomeMessage(msg, description) {
    // Create elements
    const rowDiv = document.createElement('div');
    rowDiv.classList.add('row', 'page-titles', 'mx-0', 'my-0', 'pb-0', 'text-center');
    rowDiv.style.backgroundColor = 'transparent';

    const colDiv = document.createElement('div');
    colDiv.classList.add('col-sm-12', 'pb-0');

    const welcomeDiv = document.createElement('div');
    welcomeDiv.classList.add('welcome-text');

    const heading = document.createElement('h4');
    heading.textContent = msg;

    const paragraph = document.createElement('p');
    paragraph.classList.add('mb-0');
    paragraph.textContent = description;

    // Construct the structure
    welcomeDiv.appendChild(heading);
    welcomeDiv.appendChild(paragraph);

    colDiv.appendChild(welcomeDiv);
    rowDiv.appendChild(colDiv);

    // Return the created element
    return rowDiv;
}




function createSettingsForm() {
    // Create div elements with classes
    const contentBody = document.createElement('div');
    contentBody.classList.add('content-body', 'row');

    const containerFluid = document.createElement('div');
    containerFluid.classList.add('container-fluid');

    const rowPageTitles = document.createElement('div');
    rowPageTitles.classList.add('row', 'page-titles', 'mx-0');

    const colSm6 = document.createElement('div');
    colSm6.classList.add('col-sm-12', 'p-md-0');

    const welcomeText = document.createElement('div');
    welcomeText.classList.add('welcome-text');

    const h4 = document.createElement('h4');
    h4.textContent = 'Settings';

    const row = document.createElement('div');
    row.classList.add('row');

    const colXl6 = document.createElement('div');
    colXl6.classList.add('col-xl-12', 'col-xxl-12');

    const card = document.createElement('div');
    card.classList.add('card');

    const cardHeader = document.createElement('div');
    cardHeader.classList.add('card-header');

    const cardTitle = document.createElement('h4');
    cardTitle.classList.add('card-title');
    cardTitle.textContent = 'Monthly Contributions and Fines';

    const cardBody = document.createElement('div');
    cardBody.classList.add('card-body');

    const basicForm = document.createElement('div');
    basicForm.classList.add('basic-form');

    const form = document.createElement('form');
    form.setAttribute('id', 'settingForm');

    // Create form elements
    const formGroup1 = createFormGroup('Monthly Contribution', '1000', 'monthlyCont');
    const formGroup2 = createFormGroup('Late', '50', 'lateFine');
    const formGroup3 = createFormGroup('Absent', '500', 'absentFine');
    const formGroup4 = createFormGroup('AWA', '100', 'awaFine');

    const submitBtn = document.createElement('button');
    const spinnerSpan = document.createElement('span');
    spinnerSpan.classList.add('spinner-border', 'spinner-border-sm', 'd-none')
    spinnerSpan.setAttribute('role', 'status');
    spinnerSpan.setAttribute('aria-hidden', 'true');
    spinnerSpan.setAttribute('id', 'settingSpinner');

    submitBtn.setAttribute('type', 'submit');
    submitBtn.setAttribute('id', 'updateSetting');
    submitBtn.classList.add('btn', 'btn-primary');
    submitBtn.textContent = 'Save ';
    submitBtn.appendChild(spinnerSpan);

    // Append elements to their respective parent elements
    contentBody.appendChild(containerFluid);
    containerFluid.appendChild(rowPageTitles);
    rowPageTitles.appendChild(colSm6);
    colSm6.appendChild(welcomeText);
    welcomeText.appendChild(h4);

    containerFluid.appendChild(row);
    row.appendChild(colXl6);
    colXl6.appendChild(card);
    card.appendChild(cardHeader);
    cardHeader.appendChild(cardTitle);
    card.appendChild(cardBody);
    cardBody.appendChild(basicForm);
    basicForm.appendChild(form);
    form.appendChild(formGroup1);
    form.appendChild(formGroup2);
    form.appendChild(formGroup3);
    form.appendChild(formGroup4);
    form.appendChild(submitBtn);

    // Function to create form group
    function createFormGroup(labelText, placeholderText, id) {
        const formGroup = document.createElement('div');
        formGroup.classList.add('form-group', 'row');

        const label = document.createElement('label');
        label.classList.add('col-sm-10', 'col-form-label');
        label.textContent = labelText;
        label.setAttribute('for', id);

        const divColSm10 = document.createElement('div');
        divColSm10.classList.add('col-sm-6');

        const input = document.createElement('input');
        input.setAttribute('type', 'number');
        input.classList.add('form-control');
        input.setAttribute('placeholder', placeholderText);
        input.setAttribute('min', '0');
        input.setAttribute('id', id);

        divColSm10.appendChild(input);

        formGroup.appendChild(label);
        formGroup.appendChild(divColSm10);

        return formGroup;
    }

    return contentBody;
}


// Function to create date fields
function createDateFields() {
    // Create form element
    const form = document.createElement('form');
    form.id = 'trialBalancePeriod';

    // Create div elements with classes
    const contentBody = document.createElement('div');
    contentBody.classList.add('content-body', 'row', 'text-center', 'pb-4');

    // Create From Date field
    const fromDateDiv = document.createElement('div');
    fromDateDiv.classList.add('col-md-5', 'd-flex', 'justify-content-center', 'align-items-center');

    const fromDateLabel = document.createElement('label');
    fromDateLabel.setAttribute('for', 'fromDate');
    fromDateLabel.textContent = 'From: ';

    const fromDateInput = document.createElement('input');
    fromDateInput.setAttribute('type', 'date');
    fromDateInput.setAttribute('name', 'fromDate');
    fromDateInput.classList.add('form-control');
    fromDateInput.id = 'fromDate';

    fromDateDiv.appendChild(fromDateLabel);
    fromDateDiv.appendChild(fromDateInput);

    // Create To Date field
    const toDateDiv = document.createElement('div');
    toDateDiv.classList.add('col-md-5', 'd-flex', 'justify-content-center', 'align-items-center');

    const toDateLabel = document.createElement('label');
    toDateLabel.setAttribute('for', 'toDate');
    toDateLabel.textContent = 'To: ';

    const toDateInput = document.createElement('input');
    toDateInput.setAttribute('type', 'date');
    toDateInput.setAttribute('name', 'toDate');
    toDateInput.classList.add('form-control');
    toDateInput.id = 'toDate';

    toDateDiv.appendChild(toDateLabel);
    toDateDiv.appendChild(toDateInput);

    // Create Submit button
    const submitDiv = document.createElement('div');
    submitDiv.classList.add('col-md-2', 'd-flex', 'justify-content-center', 'align-items-center');

    const submitButton = document.createElement('button');
    submitButton.setAttribute('type', 'submit');
    submitButton.id = 'datePeriod';
    submitButton.classList.add('btn', 'btn-success');
    submitButton.textContent = 'Go ';

    const spinnerSpan = document.createElement('span');
    spinnerSpan.classList.add('spinner-border', 'spinner-border-sm', 'd-none');
    spinnerSpan.setAttribute('role', 'status');
    spinnerSpan.setAttribute('aria-hidden', 'true');
    spinnerSpan.id = 'datePeriodSpinner';

    submitButton.appendChild(spinnerSpan);
    submitDiv.appendChild(submitButton);

    // Append elements to the contentBody
    contentBody.appendChild(fromDateDiv);
    contentBody.appendChild(toDateDiv);
    contentBody.appendChild(submitDiv);

    // Return contentBody element
    return contentBody;
}


function createAccountTable(accountGroups, accountBalances) {

    // Create elements
    const contentBodyDiv = document.createElement('div');
    contentBodyDiv.classList.add('content-body', 'pt-3');
  
    const containerFluidDiv = document.createElement('div');
    containerFluidDiv.classList.add('container-fluid', 'pt-0');

    // Add welcome div
    const welcomeDiv = createWelcomeMessage('Trial Balance', 'View Trial Balance');

    const rowDiv = document.createElement('div');
    rowDiv.classList.add('row', 'pt-0');
  
    const tableDiv = document.createElement('div');
    tableDiv.classList.add('table-responsive', 'pt-0');
  
    const table = document.createElement('table');
    table.classList.add('table', 'table-striped', 'text-dark', 'pt-0');
  
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');
  
    // Table headers
    const headerRow = document.createElement('tr');
    const groupHeader = document.createElement('th');
    groupHeader.textContent = 'Account Group';
    const accountsHeader = document.createElement('th');
    const balanceHeader = document.createElement('th');
    balanceHeader.textContent = 'Balance';
    accountsHeader.textContent = 'Accounts';
    headerRow.appendChild(groupHeader);
    headerRow.appendChild(accountsHeader);
    headerRow.appendChild(balanceHeader);
    thead.appendChild(headerRow);
  
    // Total row
    const totalRow = document.createElement('tr');
    const total = document.createElement('td');
    total.textContent = 'Total';
    total.setAttribute('colspan', '2');
    const totalCell = document.createElement('td');

    // Initialize the trial balance total with 0
    let tbTotal = 0;

    // Table body
    accountGroups.forEach(group => {
      const groupRow = document.createElement('tr');
      const groupCell = document.createElement('td');
      groupCell.textContent = group;
      const accountsCell = document.createElement('td');
      const accountsSelect = document.createElement('select', 'form-select', 'border-0');
      accountsSelect.style.border = 'none';
      accountsSelect.style.backgroundColor = 'transparent';

      const BalanceCell = document.createElement('td');

      // Initialize the total value with 0
      let accountGroupTotal = 0;
      
      Object.entries(accountBalances[group]).forEach(([account, balance]) => {
        accountGroupTotal += parseInt(balance);
        const option = document.createElement('option');
        option.textContent = account + ' = ' + balance;
        accountsSelect.appendChild(option);
      });
      tbTotal += accountGroupTotal;

      BalanceCell.textContent = accountGroupTotal;
      accountsCell.appendChild(accountsSelect);
      groupRow.appendChild(groupCell);
      groupRow.appendChild(accountsCell);
      groupRow.appendChild(BalanceCell);
      tbody.appendChild(groupRow);
    });
 
    // set total cell value and append to row
    totalCell.textContent = tbTotal;
    totalRow.appendChild(total);
    totalRow.appendChild(totalCell);

    // Append elements
    tbody.appendChild(totalRow);
    table.appendChild(thead);
    table.appendChild(tbody);
    tableDiv.appendChild(table);
    rowDiv.appendChild(tableDiv);
    containerFluidDiv.appendChild(welcomeDiv);
    containerFluidDiv.appendChild(rowDiv);
    contentBodyDiv.appendChild(containerFluidDiv);
  
    // Return the created content-body element
    return contentBodyDiv;
}


// Function to create date selector for income statement
function createIncomeStatementDateSelector() {
    // Create form element
    const form = document.createElement('form');
    form.id = 'incomeStatementPeriod';

    // Create div elements with classes
    const contentBody = document.createElement('div');
    contentBody.classList.add('content-body', 'row', 'text-center', 'pb-4');

    // Create From Date field
    const fromDateDiv = document.createElement('div');
    fromDateDiv.classList.add('col-md-5', 'd-flex', 'justify-content-center', 'align-items-center');

    const fromDateLabel = document.createElement('label');
    fromDateLabel.setAttribute('for', 'incomeStatementfromDate');
    fromDateLabel.textContent = 'From: ';

    const fromDateInput = document.createElement('input');
    fromDateInput.setAttribute('type', 'date');
    fromDateInput.setAttribute('name', 'incomeStatementfromDate');
    fromDateInput.classList.add('form-control');
    fromDateInput.id = 'incomeStatementfromDate';

    fromDateDiv.appendChild(fromDateLabel);
    fromDateDiv.appendChild(fromDateInput);

    // Create To Date field
    const toDateDiv = document.createElement('div');
    toDateDiv.classList.add('col-md-5', 'd-flex', 'justify-content-center', 'align-items-center');

    const toDateLabel = document.createElement('label');
    toDateLabel.setAttribute('for', 'incomeStatementToDate');
    toDateLabel.textContent = 'To: ';

    const toDateInput = document.createElement('input');
    toDateInput.setAttribute('type', 'date');
    toDateInput.setAttribute('name', 'incomeStatementToDate');
    toDateInput.classList.add('form-control');
    toDateInput.id = 'incomeStatementToDate';

    toDateDiv.appendChild(toDateLabel);
    toDateDiv.appendChild(toDateInput);

    // Create Submit button
    const submitDiv = document.createElement('div');
    submitDiv.classList.add('col-md-2', 'd-flex', 'justify-content-center', 'align-items-center');

    const submitButton = document.createElement('button');
    submitButton.setAttribute('type', 'submit');
    submitButton.id = 'incomeStatementDatePeriod';
    submitButton.classList.add('btn', 'btn-success');
    submitButton.textContent = 'Go ';

    const spinnerSpan = document.createElement('span');
    spinnerSpan.classList.add('spinner-border', 'spinner-border-sm', 'd-none');
    spinnerSpan.setAttribute('role', 'status');
    spinnerSpan.setAttribute('aria-hidden', 'true');
    spinnerSpan.id = 'datePeriodSpinner';

    submitButton.appendChild(spinnerSpan);
    submitDiv.appendChild(submitButton);

    // Append elements to the contentBody
    contentBody.appendChild(fromDateDiv);
    contentBody.appendChild(toDateDiv);
    contentBody.appendChild(submitDiv);

    // Return contentBody element
    return contentBody;
}




// Function to create P&L table
function createIncomeStatementTable(accountGroups, accountBalances) {

    // Create elements
    const contentBodyDiv = document.createElement('div');
    contentBodyDiv.classList.add('content-body', 'pt-3');
  
    const containerFluidDiv = document.createElement('div');
    containerFluidDiv.classList.add('container-fluid', 'pt-0');

    // Add welcome div
    const welcomeDiv = createWelcomeMessage('Income Statement', 'View P&L');

    const rowDiv = document.createElement('div');
    rowDiv.classList.add('row', 'pt-0');
  
    const tableDiv = document.createElement('div');
    tableDiv.classList.add('table-responsive', 'pt-0');
  
    const table = document.createElement('table');
    table.classList.add('table', 'table-striped', 'text-dark', 'pt-0');
  
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');
  
    // Table headers
    const headerRow = document.createElement('tr');
    const groupHeader = document.createElement('th');
    groupHeader.textContent = 'Account Group';
    const accountsHeader = document.createElement('th');
    const balanceHeader = document.createElement('th');
    balanceHeader.textContent = 'Total';
    accountsHeader.textContent = 'Accounts';
    headerRow.appendChild(groupHeader);
    headerRow.appendChild(accountsHeader);
    headerRow.appendChild(balanceHeader);
    thead.appendChild(headerRow);
  
    // Total row
    const totalRow = document.createElement('tr');
    const total = document.createElement('td');
    total.textContent = 'Income';
    total.setAttribute('colspan', '2');
    const incomeCell = document.createElement('td');

    // Initialize the trial balance total with 0
    let income = 0;

    // Table body
    accountGroups.forEach(group => {
      const groupRow = document.createElement('tr');
      const groupCell = document.createElement('td');
      groupCell.textContent = group;
      const accountsCell = document.createElement('td');
      const accountsSelect = document.createElement('select', 'form-select', 'border-0');
      accountsSelect.style.border = 'none';
      accountsSelect.style.backgroundColor = 'transparent';

      const BalanceCell = document.createElement('td');

      // Initialize the total value with 0
      let accountGroupTotal = 0;
      
      Object.entries(accountBalances[group]).forEach(([account, balance]) => {
        accountGroupTotal += parseInt(balance);
        const option = document.createElement('option');
        option.textContent = account + ' = ' + balance;
        accountsSelect.appendChild(option);
      }); 
      income += accountGroupTotal;

      BalanceCell.textContent = accountGroupTotal;
      accountsCell.appendChild(accountsSelect);
      groupRow.appendChild(groupCell);
      groupRow.appendChild(accountsCell);
      groupRow.appendChild(BalanceCell);
      tbody.appendChild(groupRow);
    });
 
    // set total cell value and append to row
    incomeCell.textContent = income;
    totalRow.appendChild(total);
    totalRow.appendChild(incomeCell);

    // Append elements
    tbody.appendChild(totalRow);
    table.appendChild(thead);
    table.appendChild(tbody);
    tableDiv.appendChild(table);
    rowDiv.appendChild(tableDiv);
    containerFluidDiv.appendChild(welcomeDiv);
    containerFluidDiv.appendChild(rowDiv);
    contentBodyDiv.appendChild(containerFluidDiv);
  
    // Return the created content-body element
    return contentBodyDiv;
}


// Function that creates the add new account form
function addNewAccountForm() {
  // Create elements
  const contentBody = document.createElement("div");
  contentBody.classList.add("content-body");

  const containerFluid1 = document.createElement("div");
  containerFluid1.classList.add("container-fluid");

  const authincation = document.createElement("div");
  authincation.classList.add("authincation", "h-100");

  const containerFluid2 = document.createElement("div");
  containerFluid2.classList.add("container-fluid", "h-100");

  const row = document.createElement("div");
  row.classList.add("row", "justify-content-center", "h-100", "align-items-center");

  const colMd6 = document.createElement("div");
  colMd6.classList.add("col-md-6");

  const authincationContent = document.createElement("div");
  authincationContent.classList.add("authincation-content");

  const rowNoGutters = document.createElement("div");
  rowNoGutters.classList.add("row", "no-gutters");

  const colXl12 = document.createElement("div");
  colXl12.classList.add("col-xl-12");

  const authForm = document.createElement("div");
  authForm.classList.add("auth-form");

  const heading = document.createElement("h4");
  heading.classList.add("text-center", "mb-4");
  heading.textContent = "Create New Ledger";

  const form = document.createElement("form");
  form.id = "new_account_form";


  const accountNameDiv = document.createElement("div");
  accountNameDiv.classList.add("mb-3");

  const accountNameLabel = document.createElement("label");
  accountNameLabel.htmlFor = "account_name";
  accountNameLabel.classList.add("form-label");
  accountNameLabel.textContent = "Account Name";
  accountNameLabel.setAttribute('for', 'account_name');

  const accountNameInput = document.createElement("input");
  accountNameInput.type = "text";
  accountNameInput.classList.add("form-control");
  accountNameInput.id = "account_name";
  accountNameInput.name = "account_name";
  accountNameInput.required = true;

  const accountGroupDiv = document.createElement("div");
  accountGroupDiv.classList.add("mb-3");

  const accountGroupLabel = document.createElement("label");
  accountGroupLabel.htmlFor = "account_group";
  accountGroupLabel.classList.add("form-label");
  accountGroupLabel.textContent = "Account Group";
  accountGroupLabel.setAttribute('for', 'account_group');

  const accountGroupInput = document.createElement("input");
  accountGroupInput.classList.add("form-control");
  accountGroupInput.setAttribute("list", "datalistOptions");
  accountGroupInput.id = "account_group";
  accountGroupInput.name = "account_group";
  accountGroupInput.required = true;

  const dataList = document.createElement("datalist");
  dataList.id = "datalistOptions";

  const optionValues = [
    "Cash-in-hand",
    "Bank account",
    "Duties and taxes",
    "Mobile money(MPESA)",
    "Dividends",
    "Fixed assets",
    "Current assets",
    "Expenses",
    "Income",
    "Loans and advances(Asset)",
    "Loan(Liability)",
    "Liability"
  ];

  optionValues.forEach(optionValue => {
    const option = document.createElement("option");
    option.value = optionValue;
    dataList.appendChild(option);
  });

  const modalFooter = document.createElement("div");
  modalFooter.classList.add("modal-footer");

  const spinnerSpan = document.createElement('span');
  spinnerSpan.classList.add('spinner-border', 'spinner-border-sm', 'd-none');
  spinnerSpan.setAttribute('role', 'status');
  spinnerSpan.setAttribute('aria-hidden', 'true');
  spinnerSpan.id = 'newAccountSpinner';

  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.name = "Btn";
  saveButton.value = "Submit";
  saveButton.id = "newAccountForm";
  saveButton.classList.add("btn", "btn-primary");
  saveButton.textContent = "Save";

  saveButton.appendChild(spinnerSpan);

  // Append elements
  modalFooter.appendChild(saveButton);

  accountGroupDiv.appendChild(accountGroupLabel);
  accountGroupDiv.appendChild(accountGroupInput);
  accountGroupDiv.appendChild(dataList);

  accountNameDiv.appendChild(accountNameLabel);
  accountNameDiv.appendChild(accountNameInput);

  form.appendChild(accountNameDiv);
  form.appendChild(accountGroupDiv);
  form.appendChild(modalFooter);

  authForm.appendChild(heading);
  authForm.appendChild(form);

  colXl12.appendChild(authForm);
  rowNoGutters.appendChild(colXl12);
  authincationContent.appendChild(rowNoGutters);
  colMd6.appendChild(authincationContent);
  row.appendChild(colMd6);
  containerFluid2.appendChild(row);
  authincation.appendChild(containerFluid2);
  containerFluid1.appendChild(authincation);
  contentBody.appendChild(containerFluid1);

  return contentBody;
}



