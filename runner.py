from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            #EXAMPLES
            # intuit_remove = Edit_Details("INTU", "", "Alyssa Marie Li Ann Loo", date = "01/26/2022")
            # driver.exe_admin_id("intui_remove.csv", "Login", "D", intuit_remove)

            # imc_rem = Edit_Details("IMC", "Removed in CAP Audit 2022 DP298013", "Alyssa Marie Li Ann Loo", date="05/02/2022")
            # driver.exe_admin_id("spirion_read.csv", "Login", "R", imc_rem)

            # driver.exe_service_account("svc_acct.csv", "Net ID", "R")
            pass