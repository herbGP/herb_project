import glob
import os
import re
import sys
import unittest
import time, datetime
import paramiko
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
# for waiting for page transition
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import configparser
import os
import sys

Modle = {}

class MyConfigParser(configparser.ConfigParser):
    """
    set ConfigParser options for case sensitive.
    """

    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr
conf = MyConfigParser()
config = conf.read("config.ini")
SOFT_VERSION = conf.get('soft version', 'version')
DAMAIN_IP = conf.get('IP', 'DAMAIN_IP')
host_username = conf.get('IP', 'UserName')
host_password = conf.get('IP', 'Password')

class Logger1(object):
    def __init__(self, fileN ="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "w")
        # logging.FileHandler(filename=filename, mode='w', encoding='utf-8', delay=False)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

class commom_code():

    def __init__(self, driver1):
        self.driver = driver1
        self.wait = WebDriverWait(driver=self.driver, timeout=10)
        self.waitfor_text = WebDriverWait(driver=self.driver, timeout=100)


    def wait_page_transition(self):
        self.wait.until(EC.presence_of_all_elements_located)

    def wait_page_transition_for_text(self, locator, text):
        self.waitfor_text.until(EC.text_to_be_present_in_element(locator, text))

    def del_file(self, path):
        fileNames = glob.glob(path + r'/*')
        for c_path in fileNames:
            os.remove(c_path)

    def magazine_move_load(self, magazine_address):
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        slot_address_Part = magazine_address.split('-')[3]
        Dise_address = '{}-{}'.format(drawer_address, slot_address)
        exmagazine_Address = '{}-{}-{}'.format(module_address, drawer_address, slot_address)
        try:
            self.driver.find_element(By.LINK_TEXT, 'Move Magazine').click()
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[7]').click()
            time.sleep(0.5)
            self.driver.find_element(By.LINK_TEXT, 'Move Magazine').click()
        time.sleep(1)
        box_ele = self.driver.find_element(By.ID, 'boxA')
        box_ele.find_element(By.LINK_TEXT, module_address).click()
        time.sleep(1)
        self.wait_page_transition()
        box_ele.find_element(By.XPATH, '//*[text()="%s"]//..' % Dise_address).find_element(By.TAG_NAME, 'input').click()
        box_ele.find_element(By.XPATH, '//*[text()="%s"]//..' % slot_address_Part).find_element(By.TAG_NAME, 'input').click()
        time.sleep(1)
        self.driver.find_element(By.NAME, 'move_load').click()
        a = self.driver.switch_to.alert
        a.accept()
        self.wait_page_transition()
        time.sleep(1)
        while (1):
            if self.driver.find_element(By.NAME, 'move_load').get_attribute('value') == 'Load >>':
                break
            else:
                time.sleep(1)
                continue

    def magazine_move_eject(self):
        try:
            self.driver.find_element(By.LINK_TEXT, 'Move Magazine').click()
            self.wait_page_transition()
            time.sleep(1)
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[7]').click()
            self.wait_page_transition()
            time.sleep(1)
            self.driver.find_element(By.LINK_TEXT, 'Move Magazine').click()
            self.wait_page_transition()
            time.sleep(1)
        self.driver.find_element(By.LINK_TEXT, 'Move Magazine').click()
        self.driver.find_element(By.NAME, 'move_eject').click()
        time.sleep(0.8)
        a = self.driver.switch_to.alert
        a.accept()
        if SOFT_VERSION == 'DA4':
            self.wait_page_transition_for_text(
                ('xpath', '/html/body/div[2]/div[2]/form/div/div[2]/div[2]/table/tbody/tr[3]/td'), 'No Disc')
        else:
            self.wait_page_transition_for_text(
                ('xpath', '/html/body/div[2]/div[2]/form/div/div[2]/div[2]/table/tbody/tr[4]/td'), 'No Disc')

    def magazine_msg_test_smart(self, magazine_address):
        conf = MyConfigParser()
        config = conf.read("config.ini")
        soft_version = conf.get('soft version', 'version')
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        try:
            slot_address_Part = magazine_address.split('-')[3]
        except:
            pass
        Dise_address = '{}-{}'.format(drawer_address, slot_address)
        drawer_address_position = drawer_address[0]
        drawer_address_number = int(drawer_address[-1])
        slot_address_number = int(slot_address)
        if soft_version == 'DA4':
            drawer_address_number_in_row = str((drawer_address_number * 3) + (slot_address_number // 5) + 1)
        elif soft_version == 'DA3':
            drawer_address_number_in_row = str((drawer_address_number * 3) + (slot_address_number // 5) + 1)
        else:
            drawer_address_number_in_row = None
        drawer_address_number_in_L = str((slot_address_number % 5) + 1)
        drawer_address_number_in_R = str(10 - (slot_address_number - 4 ** ((slot_address_number - 1) // 4)))
        # self.login('Service', SERVICE_PASSWORD)

        magazine_table_list = self.driver.find_elements(By.CLASS_NAME, 'magazine_table')
        for i, j in zip(range(len(magazine_table_list)), range(len(magazine_table_list), 0, -1)):
            Modle[chr(ord('A') + i)] = i + 1
        c = Modle[module_address]
        magazine_table_ele = self.driver.find_element(By.XPATH, "//div[@id='id_drawer_magazine%s']/preceding-sibling::table[1]" % Modle[module_address])
        self.driver.execute_script("arguments[0].scrollIntoView(false);", magazine_table_ele)
        if drawer_address_position == 'L':
            magazine_ele = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]' % (drawer_address_number_in_row, drawer_address_number_in_L))
            magazine_status = magazine_ele.text
            magazine_font_color = magazine_ele.value_of_css_property('color')
        elif drawer_address_position == 'R':
            magazine_ele = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]' % (drawer_address_number_in_row, drawer_address_number_in_R))
            magazine_status = magazine_ele.text
            magazine_font_color = magazine_ele.value_of_css_property('color')
        else:
            magazine_status = None
            magazine_font_color = None
        self.wait_page_transition()
        time.sleep(0.5)
        return magazine_status, magazine_font_color

    def magazine_msg_test(self, magazine_address):
        global Modle
        conf = MyConfigParser()
        config = conf.read("config.ini")
        soft_version = conf.get('soft version', 'version')
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        try:
            slot_address_Part = magazine_address.split('-')[3]
        except:
            pass
        Dise_address = '{}-{}'.format(drawer_address, slot_address)
        drawer_address_position = drawer_address[0]
        drawer_address_number = int(drawer_address[-1])
        slot_address_number = int(slot_address)
        if soft_version == 'DA4':
            drawer_address_number_in_row = str((drawer_address_number * 3) + (slot_address_number // 5))
        elif soft_version == 'DA3':
            drawer_address_number_in_row = str((drawer_address_number * 3) + 1 + (slot_address_number // 5))
        else:
            drawer_address_number_in_row = None
        drawer_address_number_in_L = str((slot_address_number % 5) + 1)
        drawer_address_number_in_R = str(10 - (slot_address_number - 4 ** ((slot_address_number - 1) // 4)))
        # self.login('Service', SERVICE_PASSWORD)
        try:
            self.driver.find_element(By.LINK_TEXT, 'Magazine').click()
            self.wait_page_transition()
            time.sleep(1)
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]').click()
            self.wait_page_transition()
            time.sleep(1)
            self.driver.find_element(By.LINK_TEXT, 'Magazine').click()
            self.wait_page_transition()
            time.sleep(1)
        magazine_table_list = self.driver.find_elements(By.CLASS_NAME, 'magazine_table')
        for i, j in zip(range(len(magazine_table_list)), range(len(magazine_table_list), 0, -1)):
            Modle[chr(ord('A') + i)] = i + 1
        c = Modle[module_address]
        magazine_table_ele = self.driver.find_element(By.XPATH, "//div[@id='id_drawer_magazine%s']/preceding-sibling::table[1]" % Modle[module_address])
        self.driver.execute_script("arguments[0].scrollIntoView(false);", magazine_table_ele)
        if drawer_address_position == 'L':
            try:
                magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]/a' % (drawer_address_number_in_row, drawer_address_number_in_L)).click()
                self.wait_page_transition()
                time.sleep(0.5)
                magazine_status = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]/a' % (drawer_address_number_in_row, drawer_address_number_in_L)).text
            except:
                magazine_status = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]' % (drawer_address_number_in_row, drawer_address_number_in_L)).text
        elif drawer_address_position == 'R':
            try:
                magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]/a' % ( drawer_address_number_in_row, drawer_address_number_in_R)).click()
                self.wait_page_transition()
                time.sleep(0.5)
                magazine_status = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]/a' % (drawer_address_number_in_row, drawer_address_number_in_R)).text
            except:
                magazine_status = magazine_table_ele.find_element(By.XPATH, './tbody/tr[%s]/td[%s]' % (drawer_address_number_in_row, drawer_address_number_in_R)).text
        else:
            magazine_status = None
        self.wait_page_transition()
        time.sleep(0.5)
        if magazine_status == 'Unknown' or magazine_status == 'Vacant':
            magazine_msg1_list = None
            magazine_msg2_list = None
            magazine_msg3_list = None
        else:
            magazine_msg_ele = self.driver.find_element(By.XPATH, "//div[@id='id_drawer_magazine%s']" % Modle[module_address])
            table_len = len(magazine_msg_ele.find_elements(By.TAG_NAME, 'table'))
            self.driver.execute_script("arguments[0].scrollIntoView(false);", magazine_msg_ele.find_elements(By.TAG_NAME, 'table')[table_len - 1])
            magazine_msg_ele1 = magazine_msg_ele.find_elements(By.TAG_NAME, 'table')[0]
            magazine_msg1 = magazine_msg_ele1.find_elements(By.TAG_NAME, 'td')
            magazine_msg1_list = []
            for i in range(0, len(magazine_msg1)):
                magazine_msg1_list.append(magazine_msg1[i].text)
            magazine_msg_ele2 = magazine_msg_ele.find_elements(By.TAG_NAME, 'table')[1]
            magazine_msg2 = magazine_msg_ele2.find_elements(By.TAG_NAME, 'td')
            magazine_msg2_list = []
            for i in range(0, len(magazine_msg2)):
                magazine_msg2_list.append(magazine_msg2[i].text)
            magazine_msg_ele3 = magazine_msg_ele.find_elements(By.TAG_NAME, 'table')[2]
            magazine_msg3_rows = magazine_msg_ele3.find_elements(By.TAG_NAME, 'tr')
            magazine_msg3_cols = magazine_msg3_rows[1].find_elements(By.TAG_NAME, 'td')
            magazine_msg3_list = [[0] * len(magazine_msg3_cols) for p in range(len(magazine_msg3_rows) - 1)]
            # print(magazine_msg3_list)
            for i in range(0, len(magazine_msg3_rows) - 1):
                magazine_msg3_cols = magazine_msg3_rows[i + 1].find_elements(By.TAG_NAME, 'td')
                for j in range(0, len(magazine_msg3_cols)):
                    magazine_msg3_list[i][j] = magazine_msg3_cols[j].text
        return magazine_msg1_list, magazine_msg2_list, magazine_msg3_list, magazine_status

    def magazine_open_drawer(self, magazine_address):
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        drawer_position = list(drawer_address)[0].lower()
        drawer_number = list(drawer_address)[1]
        try:
            self.driver.find_element(By.LINK_TEXT, 'Open Drawer').click()
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[5]').click()
            self.wait_page_transition()
            time.sleep(1)
            self.driver.find_element(By.LINK_TEXT, 'Open Drawer').click()
        magazine_table_list = self.driver.find_elements(By.TAG_NAME, 'table')
        for i, j in zip(range(len(magazine_table_list)), range(len(magazine_table_list), 0, -1)):
            Modle[chr(ord('A') + i)] = i + 1
        Module_dic = Modle
        id_address = 'unlock_{}{}{}'.format(drawer_position, Module_dic[module_address], drawer_number)
        selected_drawer = self.driver.find_element(By.ID, id_address)
        selected_drawer.click()
        self.wait_page_transition()
        self.driver.find_element(By.NAME, 'request').click()
        a = self.driver.switch_to.alert
        a.accept()
        self.wait_page_transition()

    def magazine_close_drawer(self):

        try:
            self.driver.find_element(By.LINK_TEXT, 'Open Drawer').click()
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[5]').click()
            self.wait_page_transition()
            time.sleep(1)
            self.driver.find_element(By.LINK_TEXT, 'Open Drawer').click()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=DAMAIN_IP, username=host_username, password=host_password)
        stdin, stdout, stderr = ssh.exec_command('rm /var/lib/damain/emu/drawer_open.txt')
        print(stdout)
        ssh.close()
        self.driver.find_element(By.NAME, 'finish').click()
        a = self.driver.switch_to.alert
        acmsg = a.text
        a.accept()
        self.wait_page_transition()



    def magazine_perform_inventory(self, magazine_address, scan_level):
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        try:
            self.driver.find_element(By.LINK_TEXT, 'Perform Inventory').click()
            self.wait_page_transition()
            time.sleep(1)
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[5]').click()
            self.wait_page_transition()
            time.sleep(1)
            self.driver.find_element(By.LINK_TEXT, 'Perform Inventory').click()
            self.wait_page_transition()
            time.sleep(1)
        if scan_level == 'All':
            Select(self.driver.find_element(By.NAME, 'select_scan')).select_by_visible_text(scan_level)
            # self.driver.find_element(By.NAME, 'select_scan').send_keys(scan_level)
            self.driver.find_element(By.NAME, 'commit').click()
            a = self.driver.switch_to.alert
            a.accept()
        elif scan_level == 'Select Drawer':
            Select(self.driver.find_element(By.NAME, 'select_scan')).select_by_visible_text(scan_level)
            Select(self.driver.find_element(By.NAME, 'module')).select_by_visible_text(module_address)
            Select(self.driver.find_element(By.NAME, 'drawer')).select_by_visible_text(drawer_address)
            self.driver.find_element(By.NAME, 'commit').click()
            a = self.driver.switch_to.alert
            a.accept()
        elif scan_level == 'Select Slot':
            Select(self.driver.find_element(By.NAME, 'select_scan')).select_by_visible_text(scan_level)
            Select(self.driver.find_element(By.NAME, 'module')).select_by_visible_text(module_address)
            Select(self.driver.find_element(By.NAME, 'drawer')).select_by_visible_text(drawer_address)
            Select(self.driver.find_element(By.NAME, 'slot')).select_by_visible_text(slot_address)
            self.driver.find_element(By.NAME, 'commit').click()
            a = self.driver.switch_to.alert
            a.accept()
        else:
            pass
        time.sleep(1)
        self.wait_page_transition_for_text(('xpath', '/html/body/div[2]/div[3]/div/table/tbody/tr[4]/td[2]'), '-')

    def magazine_check_disc_condition(self, magazine_address):
        module_address = magazine_address.split('-')[0]
        drawer_address = magazine_address.split('-')[1]
        slot_address = magazine_address.split('-')[2]
        slot_address_Part = magazine_address.split('-')[3]
        Dise_address = '{}-{}'.format(drawer_address, slot_address)
        exmagazine_Address = '{}-{}-{}'.format(module_address, drawer_address, slot_address)
        try:
            self.driver.find_element(By.LINK_TEXT, 'Check Disc Condition').click()
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[5]').click()
            time.sleep(0.5)
            self.driver.find_element(By.LINK_TEXT, 'Check Disc Condition').click()
        time.sleep(1)
        box_ele = self.driver.find_element(By.ID, 'boxA')
        box_ele.find_element(By.LINK_TEXT, module_address).click()
        time.sleep(1)
        self.wait_page_transition()
        box_ele.find_element(By.XPATH, '//*[text()="%s"]//..' % Dise_address).find_element(By.TAG_NAME, 'input').click()
        box_ele.find_element(By.XPATH, '//*[text()="%s"]//..' % slot_address_Part).find_element(By.TAG_NAME,
            'input').click()
        time.sleep(1)
        self.driver.find_element(By.NAME, 'check_disc_condition_exe').click()
        a = self.driver.switch_to.alert
        a.accept()
        self.wait_page_transition()


    def magazine_check_disc_condition_cannel(self):
        try:
            self.driver.find_element(By.LINK_TEXT, 'Check Disc Condition').click()
        except:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[5]').click()
            time.sleep(0.5)
            self.driver.find_element(By.LINK_TEXT, 'Check Disc Condition').click()
        self.driver.find_element(By.NAME, 'check_cancel_exe').click()
        a = self.driver.switch_to.alert
        a.accept()
        self.wait_page_transition()
        self.driver.implicitly_wait(20)
        while (1):
            accheck_cancel_button_name = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/form/div[1]/table/tbody/tr/td[1]/input').get_attribute('value')
            result = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/table/tbody/tr[4]/td[2]').text
            if result == 'Transport' and accheck_cancel_button_name == 'Cancel':
                time.sleep(30)
                self.driver.refresh()
                print('refresh page and wait for checking')
                continue
            elif result == '-' and accheck_cancel_button_name == 'Execute':
                break
            else:
                continue