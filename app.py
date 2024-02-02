from flask import Flask, render_template, request
# from flask import render_template_string

app = Flask(__name__)

class Bank:
    def __init__(self):
        self.accounts = {}
        self.users = {'admin': 'admin123'}
        
    def authenticate(self, username, password):
        return username in self.users and self.users[username] == password

    def create_account(self, username, password, account_number, name, balance=0):
        if self.authenticate(username, password):
            if account_number not in self.accounts:
                self.accounts[account_number] = {'name': name, 'balance': balance, 'transactions': []}
                return f"Account created for {name} with account number {account_number}"
            else:
                return "Account with this account number already exists."
        else:
            return "Authentication failed. Invalid username or password."

    def get_account_details(self, account_number):
        if account_number in self.accounts:
            return self.accounts[account_number]
        else:
            return "Account not found."

    def get_all_accounts(self):
        return self.accounts

    def update_account(self, username, password, account_number, name=None, balance=None):
        if self.authenticate(username, password):
            if account_number in self.accounts:
                if name:
                    self.accounts[account_number]['name'] = name
                if balance is not None:
                    self.accounts[account_number]['balance'] = balance
                return "Account updated successfully."
            else:
                return "Account not found."
        else:
            return "Authentication failed. Invalid username or password."

    def close_account(self, username, password, account_number):
        if self.authenticate(username, password):
            if account_number in self.accounts:
                del self.accounts[account_number]
                return "Account closed successfully."
            else:
                return "Account not found."
        else:
            return "Authentication failed. Invalid username or password."

    def deposit(self, account_number, amount):
        if account_number in self.accounts:
            self.accounts[account_number]['balance'] += amount
            self.accounts[account_number]['transactions'].append(f"Deposit: +${amount:.2f}")
            return f"Amount ${amount:.2f} deposited successfully. New balance: ${self.accounts[account_number]['balance']:.2f}"
        else:
            return "Account not found."

    def withdraw(self, account_number, amount):
        if account_number in self.accounts:
            if self.accounts[account_number]['balance'] >= amount:
                self.accounts[account_number]['balance'] -= amount
                self.accounts[account_number]['transactions'].append(f"Withdrawal: -${amount:.2f}")
                return f"Amount ${amount:.2f} withdrawn successfully. New balance: ${self.accounts[account_number]['balance']:.2f}"
            else:
                return "Insufficient funds."
        else:
            return "Account not found."

    def get_transaction_history(self, account_number):
        if account_number in self.accounts:
            return self.accounts[account_number]['transactions']
        else:
            return "Account not found."
        
    def generate_reports(self):
        report = "Bank Management System Report:\n"
        for account_number, details in self.accounts.items():
            report += f"\nAccount Number: {account_number}\n"
            report += f"Account Holder: {details['name']}\n"
            report += f"Balance: ${details['balance']:.2f}\n"
            report += f"Transaction History: {details['transactions']}\n"
        return report
    
    def grant_loan(self, username, password, account_number, loan_amount):
        if self.authenticate(username, password):
            if account_number in self.accounts:
                loan_details = {'loan_amount': loan_amount, 'remaining_amount': loan_amount, 'repayments': []}
                self.accounts[account_number]['loan'] = loan_details
                return f"Loan granted successfully. Remaining loan amount: ${loan_amount:.2f}"
            else:
                return "Account not found."
        else:
            return "Authentication failed. Invalid username or password."

    def repay_loan(self, username, password, account_number, repayment_amount):
        if self.authenticate(username, password):
            if account_number in self.accounts and 'loan' in self.accounts[account_number]:
                remaining_amount = self.accounts[account_number]['loan']['remaining_amount']
                if repayment_amount > 0 and remaining_amount >= repayment_amount:
                    self.accounts[account_number]['loan']['remaining_amount'] -= repayment_amount
                    self.accounts[account_number]['loan']['repayments'].append(repayment_amount)
                    return f"Loan repayment of ${repayment_amount:.2f} successful. Remaining loan amount: ${self.accounts[account_number]['loan']['remaining_amount']:.2f}"
                else:
                    return "Invalid repayment amount or remaining loan amount is less than the repayment amount."
            else:
                return "Account not found or no loan associated with the account."
        else:
            return "Authentication failed. Invalid username or password."

    def get_loan_details(self, username, password, account_number):
        if self.authenticate(username, password):
            if account_number in self.accounts and 'loan' in self.accounts[account_number]:
                return self.accounts[account_number]['loan']
            else:
                return "No loan details found for the account."
        else:
            return "Authentication failed. Invalid username or password."
        
bank = Bank()

@app.route('/')
def authenticate_page():
    return render_template('authenticate.html')

@app.route('/signup', methods=['POST'])
def signup():
    signup_username = request.form['signup_username']
    signup_password = request.form['signup_password']

    # Check if the username is already taken
    if signup_username in bank.users:
        return render_template('authenticate.html', signup_error="Username already exists. Please choose a different one.")

    # Add the new user to the bank's users
    bank.users[signup_username] = signup_password

    # Redirect to the sign-in page
    return render_template('authenticate.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']
    authenticated = bank.authenticate(username, password)

    if authenticated:
        return render_template('dashboard.html', username=username)
    else:
        return render_template('authenticate.html', error="Invalid username or password")

@app.route('/create_account', methods=['POST'])
def create_account():
    account_number = request.form['account_number']
    name = request.form['name']
    result_create_account = bank.create_account("admin", "admin123", account_number, name)
    return render_template('dashboard.html', username="admin", result_create_account=result_create_account)

@app.route('/display_account_details', methods=['POST'])
def display_account_details():
    account_number = request.form['account_number']
    account_details = bank.get_account_details(account_number)
    return render_template('dashboard.html', username="admin", account_details=account_details)


@app.route('/update_account', methods=['POST'])
def update_account():
    account_number = request.form['account_number']
    name = request.form['name']
    balance = float(request.form['balance'])
    result_update_account = bank.update_account("admin", "admin123", account_number, name, balance)
    return render_template('dashboard.html', username="admin", result_update_account=result_update_account)

@app.route('/close_account', methods=['POST'])
def close_account():
    account_number = request.form['account_number']
    result_close_account = bank.close_account("admin", "admin123", account_number)
    return render_template('dashboard.html', username="admin", result_close_account=result_close_account)

@app.route('/deposit', methods=['POST'])
def deposit():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])
    result_deposit = bank.deposit(account_number, amount)
    return render_template('dashboard.html', username="admin", result_deposit=result_deposit)

@app.route('/withdraw', methods=['POST'])
def withdraw():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])
    result_withdraw = bank.withdraw(account_number, amount)
    return render_template('dashboard.html', username="admin", result_withdraw=result_withdraw)

@app.route('/transaction_history', methods=['POST'])
def transaction_history():
    account_number = request.form['account_number']
    history = bank.get_transaction_history(account_number)
    return render_template('dashboard.html', username="admin", transaction_history=history)

@app.route('/grant_loan', methods=['POST'])
def grant_loan():
    account_number = request.form['account_number']
    loan_amount = float(request.form['loan_amount'])
    result_grant_loan = bank.grant_loan("admin", "admin123", account_number, loan_amount)
    return render_template('dashboard.html', username="admin", result_grant_loan=result_grant_loan)

@app.route('/repay_loan', methods=['POST'])
def repay_loan():
    account_number = request.form['account_number']
    repayment_amount = float(request.form['repayment_amount'])
    result_repay_loan = bank.repay_loan("admin", "admin123", account_number, repayment_amount)
    return render_template('dashboard.html', username="admin", result_repay_loan=result_repay_loan)

@app.route('/loan_details', methods=['POST'])
def loan_details():
    account_number = request.form['account_number']
    details = bank.get_loan_details("admin", "admin123", account_number)
    return render_template('dashboard.html', username="admin", loan_details=details)

@app.route('/generate_reports')
def generate_reports():
    report = bank.generate_reports()
    return render_template('dashboard.html', username="admin", report=report)

@app.route('/logout')
def logout():
    return render_template('authenticate.html')

if __name__ == "__main__":
    app.run(debug=True)
    

