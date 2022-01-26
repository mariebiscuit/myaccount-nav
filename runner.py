from myaccount_nav import *

if __name__ == '__main__':
    with open('login_details.txt') as f:
        username = f.readline()
        password = f.readline()

        with MyAccountDriver(username, password) as driver:
            #ENTER YOUR SCRIPT AFTER HERE:
            


            pass