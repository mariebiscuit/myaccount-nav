from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            #ENTER YOUR SCRIPT AFTER HERE:
            # intuit_remove = Edit_Details("INTU", "", "Alyssa Marie Li Ann Loo", date = "01/26/2022")
            # driver.exe_admin_id("intui_remove.csv", "Login", "D", intuit_remove)

            # fm_add = Edit_Details("FILE", "Added in CAP Audit 2022 DP298076", "Alyssa Marie Li Ann Loo", date="04/13/2022")
            # driver.exe_admin_id("fm_add.csv", "Email", "C", fm_add)

            # fm_rem = Edit_Details("FILE", "Removed in CAP Audit 2022 DP298076", "Alyssa Marie Li Ann Loo", date="04/13/2022")
            # driver.exe_admin_id("fm_remove.csv", "Login", "D", fm_rem)

            # exaq_add = Edit_Details("EVSS", "Added in CAP Audit 2022 DP258605", "Alyssa Marie Li Ann Loo", date="04/19/2022")
            # driver.exe_admin_id("exaq_add.csv", "Login", "C", exaq_add)

            # exaq_rem = Edit_Details("EVSS", "Removed in CAP Audit 2022 DP258605", "Alyssa Marie Li Ann Loo", date="04/19/2022")
            # driver.exe_admin_id("exaq_rem.csv", "Login", "D", exaq_rem)

            # ise_read = Edit_Details("ISE", "", "")
            # driver.exe_admin_id("ise_read.csv", "Login", "R", ise_read)

            # ise_rem = Edit_Details("ISE", "Removed in CAP Audit 2022 DP298001", "Alyssa Marie Li Ann Loo", date="04/19/2022")
            # driver.exe_admin_id("ise_rem.csv", "Login", "D", ise_rem)

            # ise_add = Edit_Details("ISE", "Added in CAP Audit 2022 DP298001", "Alyssa Marie Li Ann Loo", date="04/19/2022")
            # driver.exe_admin_id("ise_add.csv", "Login", "C", ise_add)

            # last_add = Edit_Details("LAST", "1Added in CAP Audit 2022 DP30650", "Alyssa Marie Li Ann Loo", date="04/19/2022")
            # driver.exe_admin_id("lastpass_add.csv", "Login", "C", last_add)


            # health_add = Edit_Details("HLTH", "Added in CAP Audit 2022 DP306504", "Alyssa Marie Li Ann Loo", date="04/20/2022")
            # driver.exe_admin_id("health_add.csv", "Net ID", "C", health_add)

            # health_rem = Edit_Details("HLTH", "Removed in CAP Audit 2022 DP306504", "Alyssa Marie Li Ann Loo", date="04/20/2022")
            # driver.exe_admin_id("health_rem.csv", "Login", "D", health_rem)

            gapps_read = Edit_Details("GAE", "", "")
            driver.exe_admin_id("gapps_read.csv", "Login", "R", gapps_read)


            