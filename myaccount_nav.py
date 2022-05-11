import pandas as pd
import numpy as np
import traceback
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, TimeoutException

class AdminIDLookup():
    """
    Class to encode and check user AdminID details stored from checking MyAccount page
    - :param: length: Length of the input list of users
    - :param: (Optional) Specify a student end-date, set as 05/31/2022 by default

    - :field: eservices_ind: "Active" | "Inactive"
    - :field: employment_status: "T" | "A" | "P"
    - :field: student_status: "Y" | "N"
    - :field: affiliate_status: "Y" | "N"
    - :field: end_date: If affiliate, this is their affiliate end date (MM/DD/YYYY)
    - :field: source_system: "Workday" | "OIM" | "Banner"
    - :field: completed: "Y" | "N" | "User NIL" | "AdminID NIL" | "T"  represents if requested action was completed. 
                         "Y" for completed, "N" for not completed due to invalid details (eg. terminated), "User NIL" for user not found 
                         according to search parameter, "AdminID NIL" for when application was not found in the user's list in delete mode,
                         "T" for a program time-out for any reason
    """
    def __init__(self, length : int, student_enddate: str = "05/31/2022"):
        self.eservices_ind = np.empty(length, dtype=object)
        self.employment_status = np.empty(length, dtype=object)
        self.student_status = np.empty(length, dtype=object)
        self.affiliate_status = np.empty(length, dtype=object)
        self.end_date = np.empty(length, dtype=object)
        self.source_system = np.empty(length, dtype=object)
        self.completed = np.empty(length, dtype=object)
        self.student_enddate = student_enddate

    def is_affiliate(self, index : int) -> bool:
        """ Whether index-th user in the list is an affiliate"""
        return self.affiliate_status[index] == "Y"

    def is_student(self, index: int) -> bool:
        """ Whether index-th user in the list is a student"""
        return self.source_system[index] == "Banner"
    
    def is_valid(self, index: int) -> bool:
        """ Whether index-th user in the list is valid (employed/has affiliate status)"""
        return ((self.employment_status[index] != "T") or self.is_affiliate(index)) and self.eservices_ind[index] == "Active"

    def set_student_enddate(self, index: int):
        """ If student, sets end-date to user defined student end-date"""
        assert self.is_student(index), "User should be a student"
        self.end_date[index] = self.student_enddate
    
    def to_df(self) -> pd.DataFrame:
        """ Converts AdminIDLookup object into a DataFrame """
        zipped = list(zip(self.eservices_ind, self.employment_status, self.student_status, self.affiliate_status, self.end_date, self.source_system, self.completed))
        return pd.DataFrame(zipped, columns = ['E-Services Indicator', 'Employment Status', 'Student Status', 'Affiliate Status', 'End Date', 'Source System', 'Completed'])

class SvcAcctLookup():
    """
    Class to encode and check user SvcLookup details stored from checking MyAccount page
    - :param: length: Length of the input list of users
    - :param: (Optional) Specify a student end-date, set as 05/31/2022 by default
    """
    def __init__(self, length : int):
        self.type = np.empty(length, dtype=object)
        self.sponsor = np.empty(length, dtype=object)
        self.end_date = np.empty(length, dtype=object)
        self.pwd_type = np.empty(length, dtype=object)
        self.sso = np.empty(length, dtype=object)
        self.completed = np.empty(length, dtype=object)

    def to_df(self) -> pd.DataFrame:
        """ Converts SvcAcctLookup object into a DataFrame """
        zipped = list(zip(self.type, self.sponsor, self.end_date, self.pwd_type, self.sso, self.completed))
        return pd.DataFrame(zipped, columns = ['Acct Type', 'Sponsor Name', 'End Date', 'Password Type', 'SSO Activated', 'Completed'])

class AdminIDDetails(object):
    """
    Class to encode details about making an AdminID edit
    - :param: app_code: Full, exact code for application in MyAccount (eg. "MAA") 
    - :param: comment: Desired comment to append. Programm will automatically add a full-stop before the comment to end the previous comment.
    - :param: name: Name of editing user
    - :param: expiry_reason: "Terminated" | "Revoked" | "Transfered" , "Revoked" set by default
    - :param: date: mm/dd/yyyy date to enter for expiry date
    - :param: lookup_name: (Optional) String to enter into dropdown search box for name to appear.
    """
    def __init__(self, app_code: str, comment: str, name: str, expiry_reason = "Revoked", date = "MM/DD/YYYY", lookup_name: str = ""):
        self.app_code = app_code
        self.comment = comment
        self.name = name
        self.lookup_name = name
        self.expiry_reason = expiry_reason
        self.date = date

class MyAccountDriver(object):
    
    class AdminIDNotFoundError(Exception):
        pass

    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.__driver = webdriver.Chrome()
        
        try: 
            self.__login()
        except InvalidArgumentException:
            self.__exit__(InvalidArgumentException, None, None)
        except TimeoutException:
            self.__exit__(TimeoutException, None, None)

    def __enter__(self):
        return self

    __adminid_search_param_dict = {
        'Login': 'brown_login', 
        'Email': 'brown_email', 
        'Banner ID': 'banner_id',
        'Brown ID': 'brown_id',
        'Net ID': 'brown_netid',
        'Workday ID': 'emp_wd_src_id'}

    def is_valid_adminid_search_param(self, search_param: str) -> bool:
        return search_param in self.__adminid_search_param_dict.keys()

    __svcacct_search_param_dict = {
        'Username': 'brown_login',
        'Net ID': 'net_id' 
        }

    def is_valid_svcacct_search_param(self, search_param: str) -> bool:
        return search_param in self.__svcacct_search_param_dict.keys()

    def exe_service_account(self, filename: str, search_param: str, mode: str) -> None:
        """
        Method to execute actions on service account, given that you are already logged in
        """
        assert self.is_valid_svcacct_search_param(search_param), "Usage: Search parameters accepted are 'Net ID' or 'Username'"

        filepath = "data/{}".format(filename)
        assert os.path.exists(filepath), "Filepath invalid"
    
        df = pd.read_csv(filepath_or_buffer = filepath, dtype = str)
        assert search_param in df, "Usage: One of the headers should be 'Net ID' or 'Username'"
        
        df_length = len(df[search_param].values)
        record = SvcAcctLookup(df_length)

        self.__driver.get('https://myaccount.brown.edu/serviceaccounts/list')

        if mode == "M":
            assert 'Comment' in df.columns, "Comment mode: requires a 'Comment' column in the sheet"
        elif mode == "S":
            assert 'Sponsor' in df.columns, "Sponsor mode: requires a 'Sponsor' column in the sheet"
        elif mode == "E":
            assert 'End Date' in df.columns, "End date mode: requires an 'End Date' column in the sheet"
        elif mode == "P":
            assert 'Pwd Type' in df.columns, "Pwd Type mode: requires an 'Pwd Type' column in the sheet"

        try:
            for (i, row) in tqdm(df.iterrows(), total = df_length):
                search_param_box = self.__driver.find_element_by_name(self.__svcacct_search_param_dict[search_param])
                search_param_box.send_keys(row[search_param])
                
                search_button = self.__driver.find_element_by_name("action")
                search_button.click()

                try:
                    link_button = self.__driver.find_element_by_xpath('//a[@class="btn btn-default"]')
                    id = link_button.get_attribute('href')[49:]
                    self.__driver.get("https://myaccount.brown.edu/serviceaccounts/edit/{}".format(id))

                    self.__read_svcacct(i, record)

                    if mode == "M":
                        self.__comment_svcacct(row["Comment"])
                        record.completed[i] = "Y"
                    elif mode == "S":
                        self.__sponsor_change_svcacct(row["Sponsor"])
                        record.completed[i] = "Y"
                    elif mode == "E":
                        self.__end_date_svcacct(row['End Date'])
                        record.completed[i] = "Y"
                    elif mode == "P":
                        self.__pwd_type_svcacct(row['Pwd Type'])
                        record.completed[i] = "Y"
                    elif mode == "R":
                        record.completed[i] = "Y"
                                 
                except NoSuchElementException:
                    record.completed[i] = "Acct NIL"

                except TimeoutException:
                    record.completed[i] = "T"
                    
                finally: 
                    self.__driver.get('https://myaccount.brown.edu/serviceaccounts/list')

        except KeyboardInterrupt:
            print("Operation terminating, exporting current status...")
        
        finally:
            filename = os.path.basename(filepath)

            if mode == "M":
                output_name = "{}_commented.csv".format(os.path.splitext(filename)[0])
            elif mode == "R":
                output_name = "{}_read.csv".format(os.path.splitext(filename)[0])
            elif mode == "P":
                output_name = "{}_pwdtypechange.csv".format(os.path.splitext(filename)[0])
            elif mode == "E":
                output_name = "{}_enddatechange.csv".format(os.path.splitext(filename)[0])
            elif mode == "S":
                output_name = "{}_sponsorchange.csv".format(os.path.splitext(filename)[0])

            #Export file
            df = pd.concat([df, record.to_df()], axis = 1)
            df.to_csv("output/{}".format(output_name) , index = False)

            #Print concluding statement
            if mode == "M":
                print("Comment Service Account: Completed")
            elif mode == "R":
                print("Read Service Account: Completed")
            elif mode == "P":
                print("Change PW Type: Completed")
            elif mode == "E":
                print("Change End Date: Completed")
            elif mode == "S":
                print("Change Sponsor: Completed")
    
    def __read_svcacct(self, i: int, record: AdminIDLookup):
        __info_xpath_dictionary = { 'type': '//select[@id="ser_acc_type"]/option[@selected="selected"]',
                            'sponsor': '//input[@id="sponsorname"]',
                            'end_date': '//input[@name="end_date"]',
                            'pass_types': '//select[@id="pass_types"]/option[@selected="selected"]',
                            }
        try:
            record.type[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['type']).text
            record.sponsor[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['sponsor']).get_attribute('value')
            record.end_date[i] = self.__driver.find_element_by_name('end_date').get_attribute('value')
            record.pwd_type[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['pass_types']).text
            record.sso[i] = self.__driver.find_element_by_name("brown_login").get_attribute('hidden') != "hidden"

        except NoSuchElementException:
            pass

    def __pwd_type_svcacct(self, type: str) -> None:
        """
        Method to change end date for a service account
        """

        current = self.__driver.find_element_by_xpath('//select[@id="pass_types"]/option[@selected="selected"]')
        self.__driver.execute_script("arguments[0].setAttribute('selected', '""')", current)

        new = self.__driver.find_element_by_xpath('//select[@id="pass_types"]/option[contains(text(), {})]'.format(type))
        self.__driver.execute_script("arguments[0].setAttribute('selected', 'selected')", new)

        submit = self.__driver.find_element_by_name("action")
        submit.click()

        WebDriverWait(self.__driver, 20).until(EC.alert_is_present(), "Timed out waiting for confirmation")
        alert = self.__driver.switch_to.alert
        alert.accept()


    def __end_date_svcacct(self, end_date: str) -> None:
        """
        Method to change end date for a service account
        """

        end_date_box = self.__driver.find_element_by_name("end_date")
        end_date_box.clear()
        end_date_box.send_keys(end_date)

        submit = self.__driver.find_element_by_name("action")
        submit.click()

        WebDriverWait(self.__driver, 20).until(EC.alert_is_present(), "Timed out waiting for confirmation")
        alert = self.__driver.switch_to.alert
        alert.accept()

    def __comment_svcacct(self, comment: str) -> None:
        """
        Method to add a comment for a service account
        """
        comment_box = self.__driver.find_element_by_name("comments")
        comment_box.send_keys(". {}".format(comment)) 
        submit = self.__driver.find_element_by_name("action")
        submit.click()
        
        WebDriverWait(self.__driver, 20).until(EC.alert_is_present(), "Timed out waiting for confirmation")
        alert = self.__driver.switch_to.alert
        alert.accept()

    def __sponsor_change_svcacct(self, sponsor: str) -> None:
        """
        Method to change sponsor for a service account
        """
        comment_box = self.__driver.find_element_by_name("sponsor_name1")
        comment_box.send_keys(sponsor)

        sponsor_dropdown = self.__driver.find_element_by_id("ui-id-1")
        self.__driver.execute_script("arguments[0].setAttribute('style', 'display:block')", sponsor_dropdown)
        WebDriverWait(self.__driver,10).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "{}")]'.format(sponsor))))
        new_sponsor = self.__driver.find_element_by_xpath('//span[contains(text(), "{}")]/parent::*//parent::*'.format(sponsor))
        new_sponsor.click()
        
        submit = self.__driver.find_element_by_name("action")
        submit.click()

        WebDriverWait(self.__driver, 20).until(EC.alert_is_present(), "Timed out waiting for confirmation")
        alert = self.__driver.switch_to.alert
        alert.accept()

    def exe_admin_id(self, filename: str,  search_param: str = "Login", mode = "R", details: AdminIDDetails = None) -> None:
        """
        Method to execute actions on AdminID, given that you are already logged in
        - :param: filename: name of .csv file containing list of users for interacting
        - :param: search_param: "Login" | "Email" | "Banner ID" | "Brown ID" | "Net ID" | "Workday ID" representing field to use to search for users 
        - :param: mode: "C" | "R" | "D" | "P" | "M" > representing (C)reate, (R)ead, (D)elete, (P)urge, Co(M)ment AdminIDs respectively
        - :param: details: AdminIDDetails object containing necessary information for Creating or Deleting from AdminID
        """
        assert self.is_valid_adminid_search_param(search_param), "Usage: Search parameters accepted are 'Login', 'Email', 'Banner ID', 'Brown ID', 'Net ID' or 'Workday ID"

        filepath = "data/{}".format(filename)
        assert os.path.exists(filepath), "Filepath invalid"
    
        df = pd.read_csv(filepath_or_buffer = filepath, dtype = str)
        assert search_param in df, "Usage: One of the headers should be 'Login', 'Email', 'Banner ID', 'Brown ID' or 'Net ID'"

        assert mode in ["C", "R", "D", "P", "M"], 'Usage: mode has to be "C" | "R" | "D" | "P" | "M"'
        
        df_length = len(df[search_param].values)

        record = AdminIDLookup(df_length)

        self.__driver.get('https://myaccount.brown.edu/person/search')

        try:
            for (i, id_data) in tqdm(enumerate(df[search_param].values), total = df_length):
                
                search_param_box = self.__driver.find_element_by_name(self.__adminid_search_param_dict[search_param])
                search_param_box.send_keys(id_data)
                
                search_button = self.__driver.find_element_by_name("search")
                search_button.click()

                try:
                    link_button = self.__driver.find_element_by_xpath('//a[@class="btn btn-default"]')
                    id = link_button.get_attribute('href')[44:]
                    self.__driver.get("https://myaccount.brown.edu/person/overview/{}".format(id))

                    self.__read_adminid(i, record)
                    
                    if mode == "C":
                        assert details != None, "To create, please initialize an AdminIDDetails object."

                        if record.is_valid(i):
                            self.__driver.get('https://myaccount.brown.edu/person/privilegeedit/{}/-1'.format(id)) 
                            self.__create_adminnid(details, record, i)
                            record.completed[i] = "Y"
                        else:
                            record.completed[i] = "N"
                        
                    elif mode == "D":
                        assert details != None, "To delete, please initialize an AdminIDDetails object."
                        assert details.expiry_reason != "MM/DD/YYYY", "To delete, input a valid MM/DD/YYYY date in the AdminIDDetails object for date of expiry."

                        self.__driver.get('https://myaccount.brown.edu/person/privileges/{}'.format(id))
                        
                        try: 
                            self.__delete_adminid(details)
                            record.completed[i] = "Y"
                        except self.AdminIDNotFoundError:
                            record.completed[i] = "AdminID NIL"
                    
                    elif mode == "P":
                        assert details != None, "To purge, please initialize an AdminIDDetails object."

                        self.__driver.get('https://myaccount.brown.edu/person/privileges/{}'.format(id))
                        
                        try: 
                            self.__purge_adminid(details)
                            record.completed[i] = "Y"
                        except self.AdminIDNotFoundError:
                            record.completed[i] = "AdminID NIL"

                    elif mode == "R":
                        record.completed[i] = "Y" 

                    elif mode == "M":
                        assert details != None, "To comment, please initialize an AdminIDDetails object."
                        self.__driver.get('https://myaccount.brown.edu/person/privileges/{}'.format(id))
                        
                        try: 
                            self.__comment_adminid(details)
                            record.completed[i] = "Y"
                        except self.AdminIDNotFoundError:
                            record.completed[i] = "AdminID NIL"
                            
                except NoSuchElementException:
                    record.completed[i] = "User NIL"

                except TimeoutException:
                    record.completed[i] = "T"
                
                finally: 
                    self.__driver.get('https://myaccount.brown.edu/person/search')
        
        except KeyboardInterrupt:
            print("Operation terminating, exporting current status...")
        
        finally:
            filename = os.path.basename(filepath)

            if mode == "C":
                output_name = "{}_created.csv".format(os.path.splitext(filename)[0])
            elif mode == "R":
                output_name = "{}_read.csv".format(os.path.splitext(filename)[0])
            elif mode == "D":
                output_name = "{}_deleted.csv".format(os.path.splitext(filename)[0])
            elif mode == "P":
                output_name = "{}_purged.csv".format(os.path.splitext(filename)[0])
            elif mode == "M":
                output_name = "{}_commented.csv".format(os.path.splitext(filename)[0])


            #Export file
            df = pd.concat([df, record.to_df()], axis = 1)
            df.to_csv("output/{}".format(output_name) , index = False)

            #Print concluding statement
            if mode == "C":
                print("Create AdminID: Completed")
            elif mode == "R":
                print("Read AdminID: Completed")
            elif mode == "D":
                print("Delete AdminID: Completed")
            elif mode == "P":
                print("Purge AdminID: Completed")
            elif mode == "M":
                print("Comment AdminID: Completed")


    def __read_adminid(self, i: int, record: AdminIDLookup):
        """
        Method to scan MyAccount page once a user page is opened and load information
        into a AdminIDLookup object
        """
        __info_xpath_dictionary = { 'eservices_ind': '//div[@class = "row"]/div[@class = "panel panel-default"][1]/div/div[2]/div[2]/div/div',
                            'employment_status': '//div[@class = "row"]/div[@class = "panel panel-default"][3]/div/div[2]/div[2]/div/div',
                            'affiliate_status': '//div[@class = "row"]/div[@class = "panel panel-default"][7]/div/div[1]/div[1]/div/div',
                            'student_status': '//div[@class = "row"]/div[@class = "panel panel-default"][2]/div/div/div/div/div',
                            'source_system': '//div[@class = "row"]/div[@class = "panel panel-default"][1]/div/div[2]/div[1]/div/div',
                            'end_date' : '//div[@class = "row"]/div[@class = "panel panel-default"][7]/div/div[2]/div[2]/div/div'
                            }

        try:
            record.eservices_ind[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['eservices_ind']).text
            record.employment_status[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['employment_status']).text
            record.student_status[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['student_status']).text
            record.affiliate_status[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['affiliate_status']).text
            record.source_system[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['source_system']).text

            if record.is_affiliate(i):
                record.end_date[i] = self.__driver.find_element_by_xpath(__info_xpath_dictionary['end_date']).text

        except NoSuchElementException:
            pass
    
    def __comment_adminid(self, details: AdminIDDetails) -> None:
        """
        Method to bulk-add a comment for an app across multiple users
        :param: details: desired comment should be input in the details class
        """
        try:
            edit_link = self.__driver.find_element_by_xpath('//tr/td//span[contains(text(), "{}")]/ancestor::td/following-sibling::td[6]/a'.format(details.app_code)).get_attribute('href')
            self.__driver.get(edit_link)
        except NoSuchElementException:
            raise self.AdminIDNotFoundError("App to comment was not found")
        
        comment_box = self.__driver.find_element_by_name("comments")
        comment_box.send_keys(". {}".format(details.comment)) 

        delete_doneby = self.__driver.find_element_by_xpath('//span[@class = "twitter-typeahead hidden"]')
        self.__driver.execute_script("arguments[0].setAttribute('class', 'twitter-typeahead')", delete_doneby)

        editor_search_box = self.__driver.find_element_by_id("searchField")
        editor_search_box.send_keys(details.lookup_name)

        doneby_xpath = '//div[@class = "tt-dataset-my-dataset"]/span/div/p/b[contains(text(), "{}")]'.format(details.name)
        WebDriverWait(self.__driver,10).until(EC.presence_of_element_located((By.XPATH, doneby_xpath)))
        doneby_dropdown = self.__driver.find_element_by_xpath(doneby_xpath)
        doneby_dropdown.click()

        WebDriverWait(self.__driver, 20).until(EC.text_to_be_present_in_element((By.XPATH, '//p[@class = "form-control-static"]/span'), details.name))
        submit = self.__driver.find_element_by_xpath('//div[@class = "col-sm-6"]/button')
        submit.click()

    def __create_adminnid(self, details: AdminIDDetails, record: AdminIDLookup, index: int) -> None :
        """
        Method to create Admin ID entry on privilege edit page. 
        Selects app, enters comment, fills 'edited by' field, clicks submit.
        """
        
        select_app = self.__driver.find_element_by_xpath('//select/option[contains(text(),"{}")]'.format(details.app_code))
        select_app.click()

        completed_selector = Select(self.__driver.find_element_by_name("status_id"))
        completed_selector.select_by_visible_text("Complete")

        if (record.is_affiliate(index) or record.is_student(index)):

            if record.is_student(index):
                record.set_student_enddate(index)

            attn_selector = Select(self.__driver.find_element_by_name("attn_type"))
            attn_selector.select_by_visible_text("End Date") #TODO: add option?
            
            attn_date_box = self.__driver.find_element_by_name("attn_date")
            attn_date_box.clear()
                            
            attn_date_box.send_keys(record.end_date[index])

        comment_box = self.__driver.find_element_by_name("comments")
        comment_box.send_keys("{}".format(details.comment)) 

        editor_search_box = self.__driver.find_element_by_id("searchField")
        editor_search_box.send_keys(details.lookup_name)
        
        doneby_xpath = '//div[@class = "tt-dataset-my-dataset"]/span/div/p/b[contains(text(), "{}")]'.format(details.name)
        WebDriverWait(self.__driver,10).until(EC.presence_of_element_located((By.XPATH, doneby_xpath)))
        doneby_dropdown = self.__driver.find_element_by_xpath(doneby_xpath)
        doneby_dropdown.click()

        WebDriverWait(self.__driver, 20).until(EC.text_to_be_present_in_element((By.XPATH, '//p[@class = "form-control-static"]/span'), details.name))
        submit_button = self.__driver.find_element_by_xpath('//div[@class = "col-sm-6"]/button')
        submit_button.click()

    def __delete_adminid(self, details: AdminIDDetails) -> None:
        """
        Method to delete Admin ID entry from user privileges list page
        Selects app, enters comment, fills 'edited by' field, clears attention, fills expiry reason and date, clicks submit.
        """

        try:
            edit_link = self.__driver.find_element_by_xpath('//tr/td//span[contains(text(), "{}")]/ancestor::td/following-sibling::td[6]/a'.format(details.app_code)).get_attribute('href')
            self.__driver.get(edit_link)
        except NoSuchElementException:
            raise self.AdminIDNotFoundError("App to delete was not found")
        
        select_exp_reason = Select(self.__driver.find_element_by_name("exp_reason"))
        select_exp_reason.select_by_visible_text(details.expiry_reason)
                
        exp_date = self.__driver.find_element_by_name("exp_date")
        exp_date.clear()
        exp_date.send_keys(details.date)

        clear_attn = self.__driver.find_element_by_id("clearAttn")
        clear_attn.click()

        comment_box = self.__driver.find_element_by_name("comments")
        comment_box.send_keys("{}".format(details.comment)) 

        try:
            delete_doneby = self.__driver.find_element_by_xpath('//span[@class = "twitter-typeahead hidden"]')
            self.__driver.execute_script("arguments[0].setAttribute('class', 'twitter-typeahead')", delete_doneby)
        except:
            pass

        editor_search_box = self.__driver.find_element_by_id("searchField")
        editor_search_box.send_keys(details.lookup_name)

        doneby_xpath = '//div[@class = "tt-dataset-my-dataset"]/span/div/p/b[contains(text(), "{}")]'.format(details.name)
        WebDriverWait(self.__driver,10).until(EC.presence_of_element_located((By.XPATH, doneby_xpath)))
        doneby_dropdown = self.__driver.find_element_by_xpath(doneby_xpath)
        doneby_dropdown.click()

        WebDriverWait(self.__driver, 20).until(EC.text_to_be_present_in_element((By.XPATH, '//p[@class = "form-control-static"]/span'), details.name))
        submit = self.__driver.find_element_by_xpath('//div[@class = "col-sm-6"]/button')
        submit.click()

    def __purge_adminid(self, details: AdminIDDetails):
        try:
            purge_link = self.__driver.find_element_by_xpath('//tr/td//span[contains(text(), "{}")]/ancestor::td/following-sibling::td[6]/a[@class = "confirmDialog"]'.format(details.app_code)).get_attribute('href')
            self.__driver.get(purge_link)
        except NoSuchElementException:
            raise self.AdminIDNotFoundError("App to purge was not found")

    def __login(self): 
        """
        Method to log into MyAccount
        """
        self.__driver.get('https://myaccount.brown.edu/person/search')
        # Key in username
        id_box = self.__driver.find_element_by_id('username')
        id_box.send_keys(self.__username)

        # Find password box
        pass_box = self.__driver.find_element_by_id('password')
        pass_box.send_keys(self.__password)

        # Find login button
        login_button = self.__driver.find_element_by_name('_eventId_proceed')
        login_button.click()

        # if EC.presence_of_element_located((By.XPATH, '//p[@class = "form-element form-error"]')):
        #     raise InvalidArgumentException("Sorry, invalid login details")
        # else:
        WebDriverWait(self.__driver,30).until(EC.visibility_of_element_located((By.NAME, "first_name")))
    
    def __exit__(self, exc_type, exc_value, tb):
        self.__driver.quit()

        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)