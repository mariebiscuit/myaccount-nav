from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            #EXAMPLES
            # intuit_remove = Edit_Details("INTU", "", "Alyssa Marie Li Ann Loo", date = "01/26/2022")
            # driver.exe_admin_id("intui_remove.csv", "Login", "D", intuit_remove)

            # fm_add = Edit_Details("FILE", "Added in CAP Audit 2022 DP298076", "Alyssa Marie Li Ann Loo", date="04/13/2022")
            # driver.exe_admin_id("fm_add.csv", "Email", "C", fm_add)

            # fm_rem = Edit_Details("FILE", "Removed in CAP Audit 2022 DP298076", "Alyssa Marie Li Ann Loo", date="04/13/2022")
            # driver.exe_admin_id("fm_remove.csv", "Login", "D", fm_rem)

            # ise_read = Edit_Details("ISE", "", "")
            # driver.exe_admin_id("ise_read.csv", "Login", "R", ise_read)

            #ENTER YOUR SCRIPT AFTER HERE