from main import Orders
from main import db

class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self):
        if self.username == "admin" and self.password == "password":
            return True
        else:
            return False
class Signup:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def validate_username(self):
        return len(self.username) > 0

    def validate_password(self):
        return len(self.password) >= 8

    def validate_email(self):
        return '@' in self.email

    def create_account(self):
        if self.validate_username() and self.validate_password() and self.validate_email():
            return True
        else:
            return False
        
class ChangePassword:
    def __init__(self, username, old_password, new_password):
        self.username = username
        self.old_password = old_password
        self.new_password = new_password

    def validate_username(self):
        return len(self.username) > 0

    def validate_old_password(self):
        return len(self.old_password) >= 8 

    def validate_new_password(self):
        return len(self.new_password) >= 8  

    def change_password(self):
        if self.validate_username() and self.validate_old_password() and self.validate_new_password():
            return True
        else:
            return False
       
class SubmitOrder:
    def __init__(self, company_name, billboard_info, region, size, display_type, surface_type, start_date, end_date):
        self.company_name = company_name
        self.billboard_info = billboard_info
        self.region = region
        self.size = size
        self.display_type = display_type
        self.surface_type = surface_type
        self.start_date = start_date
        self.end_date = end_date

    def validate_company_name(self):
        return len(self.company_name) > 0

    def validate_billboard_info(self):
        return len(self.billboard_info) > 0

    def validate_region(self):
        return len(self.region) > 0

    def validate_size(self):
        return len(self.size) > 0

    def validate_display_type(self):
        return len(self.display_type) > 0

    def validate_surface_type(self):
        return len(self.surface_type) > 0

    def validate_dates(self):
        return True

    def create_order(self):
        if (
            self.validate_company_name() 
            and self.validate_billboard_info() 
            and self.validate_region() 
            and self.validate_size() 
            and self.validate_display_type() 
            and self.validate_surface_type() 
            and self.validate_dates()
        ):
            return True
        else:
            return False


    def changed_order(self, changed_units):
        return any(changed_units.values())
    
class PaymentStatusCheck:
    def __init__(self, order_id, action):
        self.order_id = order_id
        self.action = action

    def validate_order_id(self):
        return isinstance(self.order_id, int) and self.order_id > 0

    def validate_action(self):
        return self.action in ['accept', 'reject']

    def check_payment_status(self):
        if self.validate_order_id() and self.validate_action():
            return True  
        else:
            return False

 
