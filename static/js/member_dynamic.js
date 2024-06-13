// Create loan request form

function createLoanRequestForm () {
    // Create elements
    const contentBody = document.createElement('div');
    contentBody.classList.add('content-body');
  
    const containerFluidOuter = document.createElement('div');
    containerFluidOuter.classList.add('container-fluid');
  
    const authincationOuter = document.createElement('div');
    authincationOuter.classList.add('authincation', 'h-100');
  
    const containerFluidInner = document.createElement('div');
    containerFluidInner.classList.add('container-fluid', 'h-100');
  
    const row = document.createElement('div');
    row.classList.add('row', 'justify-content-center', 'h-100', 'align-items-center');
  
    const colMd12 = document.createElement('div');
    colMd12.classList.add('col-md-12');
  
    const authincationContent = document.createElement('div');
    authincationContent.classList.add('authincation-content');
  
    const rowNoGutters = document.createElement('div');
    rowNoGutters.classList.add('row', 'no-gutters');
  
    const colXl12 = document.createElement('div');
    colXl12.classList.add('col-xl-12');
  
    const authForm = document.createElement('div');
    authForm.classList.add('auth-form');
  
    // Add content to elements
    authForm.innerHTML = `
        <h4 class="text-center mb-4">Loan Request Form</h4>
        <form id="loanForm">
            <div class="form-group">
                <label for="loanAmount">Loan Amount</label>
                <input type="number" class="form-control" id="loanAmount" placeholder="Enter loan amount" min="1" name="loanAmount" required>
            </div>
            <div class="form-group">
                <label for="loanCategory">Loan Category</label>
                <select class="form-control" id="loanCategory" required>
                    <option value="0">Up to ksh 30,000 (2 months)</option>
                    <option value="1">Above ksh 30,000 (4 months)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="amountToRepay">Amount to Repay</label>
                <input type="text" class="form-control" id="amountToRepay" name="amountToRepay" readonly>
            </div>
            <p class="btn btn-primary" id="submitLoanRequest">
            Submit
            <span class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true" id="loanRequestSpinner"></span>
            </p>
        </form>
    `;
  
    // Append elements to each other
    colXl12.appendChild(authForm);
    rowNoGutters.appendChild(colXl12);
    authincationContent.appendChild(rowNoGutters);
    colMd12.appendChild(authincationContent);
    row.appendChild(colMd12);
    containerFluidInner.appendChild(row);
    authincationOuter.appendChild(containerFluidInner);
    containerFluidOuter.appendChild(authincationOuter);
    contentBody.appendChild(containerFluidOuter);
  
    return contentBody;
  }