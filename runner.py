from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            # ENTER YOUR SCRIPT AFTER HERE:
            sample_create = Edit_Details("ABC", "This is the comment.", "Josiah Carberry")
            # driver.exe_admin_id('FILENAME.csv', "Email", "C", sample_create)

            # sample_delete = Edit_Details("ABC", "This is the comment.", "Josiah Carberry", "josiah car", expiry_reason = "Revoked", date = "01/26/2022" )
            # driver.exe_admin_id('FILENAME.csv', "Email", "D", sample_delete)