from myaccount_nav import *

# modify sponsor for a given app
# change end date for service account
# change account password type -- change options
# add comments at the bottom

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

            # unix_add = Edit_Details("UNI", "Added in CAP Audit 2022 DP298022", "Alyssa Marie Li Ann Loo", date="04/25/2022")
            # driver.exe_admin_id("unix_add.csv", "Login", "C", unix_add)

            # github_read = Edit_Details("GIT", "Added in CAP Audit 2022 DP298022", "Alyssa Marie Li Ann Loo", date="04/25/2022")
            # driver.exe_admin_id("github_read.csv", "Login", "R", github_read)

            # clear_read = Edit_Details("CLEAR", "Added in CAP Audit 2022 DP298022", "Alyssa Marie Li Ann Loo", date="04/25/2022")
            # driver.exe_admin_id("clear_read.csv", "Login", "R", clear_read)

            # zkteco_add = Edit_Details("ZKTEC", "Added in CAP Audit 2022 DP298003", "Alyssa Marie Li Ann Loo", date="05/02/2022")
            # driver.exe_admin_id("zkteco_add.csv", "Workday ID", "C", zkteco_add)

            imc_rem = Edit_Details("IMC", "Removed in CAP Audit 2022 DP298013", "Alyssa Marie Li Ann Loo", date="05/02/2022")
            driver.exe_admin_id("spirion_read.csv", "Login", "R", imc_rem)