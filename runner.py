from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            #EXAMPLES
            # zoom_remove = AdminIDDetails("ZOOM", "Added in CAP Audit Test", "Alyssa Marie Li Ann Loo", expiry_reason="Revoked", date="11/05/2022")
            # driver.exe_admin_id("test.csv", "Login", "R", zoom_remove)

            # driver.exe_service_account("svc_acct.csv", "Net ID", "R")


            pass