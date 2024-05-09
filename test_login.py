import unittest
from unittest.mock import patch
from main import app
from signup import Login,Signup,SubmitOrder, ChangePassword, PaymentStatusCheck

class TestLogin(unittest.TestCase):
    def test_correct_credentials(self):
        login = Login("admin", "password")
        self.assertTrue(login.authenticate())

    def test_incorrect_credentials(self):
        login = Login("admin", "wrongpassword")
        self.assertFalse(login.authenticate())

class TestSignup(unittest.TestCase):
    def test_successful_signup(self):
        signup = Signup("testuser", "password123", "test@example.com")
        self.assertTrue(signup.create_account())

    def test_invalid_signup(self):
        signup = Signup("", "", "invalidemail")
        self.assertFalse(signup.create_account())

class TestChangePassword(unittest.TestCase):
    def test_successful_password_change(self):
        change_password = ChangePassword("testuser", "oldpassword", "newpassword123")
        self.assertTrue(change_password.change_password())

    def test_invalid_password_change(self):
        change_password = ChangePassword("", "", "")
        self.assertFalse(change_password.change_password())  

class TestSubmitOrder(unittest.TestCase):
    def test_valid_order_creation(self):
        order = SubmitOrder(
            company_name="ABC Company",
            billboard_info="Info",
            region="Region",
            size="Large",
            display_type="Digital",
            surface_type="LED",
            start_date="2024-04-15",
            end_date="2024-04-20"
        )
        self.assertTrue(order.create_order())

    def test_invalid_order_creation_missing_company_name(self):
        order = SubmitOrder(
            company_name="", 
            billboard_info="Info",
            region="Region",
            size="Large",
            display_type="Digital",
            surface_type="LED",
            start_date="2024-04-15",
            end_date="2024-04-20"
        )
        self.assertFalse(order.create_order())

    def test_changed_order(self):
        order = SubmitOrder(
            company_name="ABC Company",
            billboard_info="Info",
            region="Region",
            size="Large",
            display_type="Digital",
            surface_type="LED",
            start_date="2024-04-15",
            end_date="2024-04-20"
        )
        changed_units = {
            "company_name": True,
            "billboard_info": False,
            "region": False,
            "size": False,
            "display_type": False,
            "surface_type": False,
            "start_date": False,
            "end_date": False
        }
        self.assertTrue(order.changed_order(changed_units))

class TestPaymentStatusCheck(unittest.TestCase):
    def test_valid_order_id(self):
        payment_check = PaymentStatusCheck(order_id=1, action='accept')
        self.assertTrue(payment_check.validate_order_id())

    def test_invalid_order_id(self):
        payment_check = PaymentStatusCheck(order_id='invalid', action='accept')
        self.assertFalse(payment_check.validate_order_id())

    def test_valid_action(self):
        payment_check = PaymentStatusCheck(order_id=1, action='accept')
        self.assertTrue(payment_check.validate_action())

    def test_invalid_action(self):
        payment_check = PaymentStatusCheck(order_id=1, action='invalid')
        self.assertFalse(payment_check.validate_action())

    def test_check_payment_status_valid(self):
        payment_check = PaymentStatusCheck(order_id=1, action='accept')
        self.assertTrue(payment_check.check_payment_status())

    def test_check_payment_status_invalid_order_id(self):
        payment_check = PaymentStatusCheck(order_id='invalid', action='accept')
        self.assertFalse(payment_check.check_payment_status())

    def test_check_payment_status_invalid_action(self):
        payment_check = PaymentStatusCheck(order_id=1, action='invalid')
        self.assertFalse(payment_check.check_payment_status())
   


if __name__ == '__main__':
    unittest.main()
