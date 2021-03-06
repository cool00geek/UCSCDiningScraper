#!/usr/bin/env python3

import sys
import argparse
import requests
import datetime
import os
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime as dt
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.phantomjs import PhantomJsDriverManager

cowell_names = ['cowell', 'cowell college', 'stevenson', 'stevenson college', 'cowell stevenson']
crown_names = ['crown', 'crown college', 'merrill', 'merrill college', 'crown merrill']
porter_names = ['porter', 'porter college', 'kresge', 'kresge college', 'porter kresge']
rcc_names = ['rcc', 'rachel carson', 'rachel carson college', 'oakes', 'oakes college', 'rachel']
c9_names = ["c9", '9', 'c10', '10', 'college 9', 'college 10', 'college9', 'college10', 'college', '9/10', 'nine', 'ten']

# Taken from https://codereview.stackexchange.com/questions/25417/is-there-a-better-way-to-make-a-function-silent-on-need
class NoStdStreams(object):
    def __init__(self,stdout = None, stderr = None):
        self.devnull = open(os.devnull,'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()

class UCSCDining:
    def __init__(self):
        pass
    
    def verify_name(self, raw_name):
        college = raw_name.lower()
        if college in cowell_names:
            return True
        elif college in crown_names:
            return True
        elif college in porter_names:
            return True
        elif college in rcc_names:
            return True
        elif college in c9_names:
            return True
        return False
    
    def get_dining_hall_url(self, proper_name):
        college = proper_name.lower()
        if college in cowell_names:
            return "Cowell+Stevenson"
        elif college in crown_names:
            return "Crown+Merrill"
        elif college in porter_names:
            return "Porter+Kresge"
        elif college in rcc_names:
            return "Rachel+Carson+Oakes"
        elif college in c9_names:
            return "Colleges+Nine+%26+Ten"
        return ""
    
    def get_college_name(self, raw_name):
        college = raw_name.lower()
        if college in cowell_names:
            return "cowell"
        elif college in crown_names:
            return "crown"
        elif college in porter_names:
            return "porter"
        elif college in rcc_names:
            return "rcc"
        elif college in c9_names:
            return "c9"
        return ""
    
    def get_dining_num(self, raw_name):
        college = raw_name.lower()
        if college in cowell_names:
            return "05"
        elif college in crown_names:
            return "20"
        elif college in porter_names:
            return "25"
        elif college in rcc_names:
            return "30"
        elif college in c9_names:
            return "40"
        return ""
    
    def get_desired_meal(self, meal_name):
        meal = meal_name.lower()
        if meal == "breakfast":
            return 0
        elif meal == "lunch" or meal == "brunch":
            return 1
        elif meal == "dinner":
            return 2
        elif meal == "night" or meal == "late night" or meal == 'late':
            return 3
        else:
            return -1
        
    def get_current_meal(self):
        now = datetime.datetime.now()
        minu = now.minute
        hour = now.hour
        day = now.weekday()
        if  0 <= day <= 4 :
            if 20 <= hour < 24:
                return 3
            if 14 <= hour < 20:
                return 2
            if 12 <= hour < 14:
                return 1
            if 11 == hour and minu >= 30:
                return 1
            return 0
        else:
            if 20 <= hour < 24:
                return 3
            if 14 <= hour < 20:
                return 2
            if 10 <= hour < 14:
                return 1
            return 0
        
    def get_url(self, college, date):
        month,date,year = date.split("/")
        #url="https://nutrition.sa.ucsc.edu/menuSamp.asp?myaction=read&sName=&dtdate={month}%2F{day}%2F{year}&locationNum={num}&locationName=%20{name}+Dining+Hall&naFlag=1"
        url="https://nutrition.sa.ucsc.edu/shortmenu.aspx?sName=UC+Santa+Cruz+Dining&locationNum={num}&locationName={name}+Dining+Hall&naFlag=1&WeeksMenus=UCSC+-+This+Week%27s+Menus&myaction=read&dtdate={month}%2F{day}%2F{year}"
        return url.format(num=self.get_dining_num(college), name=self.get_dining_hall_url(college), month=str(int(month)), day=str(int(date)), year=year)
    
    # Parse the menu
    def parse_menu(self, driver, college, url, start_index):
        raw_college = college.lower()
        if college in cowell_names:
            my_college = 2 # //*[@id="locationchoices"]/ul/li[2]/a
        elif college in crown_names:
            my_college = 3
        elif college in porter_names:
            my_college=4
        elif college in rcc_names:
            my_college = 5
        elif college in c9_names:
            my_college = 1 # //*[@id="locationchoices"]/ul/li[1]/a
        else:
            exit(4)
           
        try:
            link = driver.find_element_by_xpath('//*[@id="locationchoices"]/ul/li['+ str(my_college) + ']/a')
            link.click()
        except:
            pass
        driver.get(url)
        start_index += 1
        try:
            meal_label = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[" + str(start_index) + "]/td/table/tbody/tr[1]/td/table/tbody/tr/td[1]/div")
            label = meal_label.text
        except Exception as e:
            #print(e)
            return "", list()
        items=list()
        try:
            table_elements = driver.find_elements_by_xpath("/html/body/table[2]/tbody/tr[" + str(start_index) + "]/td/table/tbody/tr[2]/td/table/tbody/tr")
            for i in range(1,len(table_elements) + 1):
                item = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[" + str(start_index) + "]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(i)+"]/td[1]/table/tbody/tr/td[1]/div/span")
                #print(item.text)
                items.append(item.text)
        except Exception as e: print(e)
        return label, items
        
        
    def print_menu(self, meal, menu):
        # Convert Late -> Late Night
        if meal == "Late":
            meal = "Late Night"
            
        if len(menu) == 0:
            return
        # Print the heading for the meal (The name and the number of dishes it has
        print(meal + ": " + str(len(menu)))
        # And print every dish in the menu
        for dish in menu:
            if not dish.strip() == "":
                print(dish.strip())

    def get_path(self):
        home = str(Path.home())
        cache_dir = home + "/.cache/UCSCDining/"
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)
        return cache_dir

    def get_filename(self, college, date):
        day = dt.strptime(date, '%m/%d/%Y')
        date = str(day.year) + "-" + str(day.month) + "-" + str(day.day)
        college_name = self.get_college_name(college)
        return date + "_" + college_name + ".txt"

    def cache(self, filename, text):
        cache_dir = self.get_path()
        menu = open(cache_dir + filename, "w")
        menu.write(text)
        menu.close()
        
    def open_driver(self):
        # 4 meals so do it 4 times
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        with NoStdStreams():
            #driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
            driver = webdriver.PhantomJS(PhantomJsDriverManager().install())
        driver.get("https://nutrition.sa.ucsc.edu/")
        return driver


def main(infile="", college="", datestr="", nocache=False, meal="", all_meals=False):

    
    dining = UCSCDining()
    using_cache = False
    
    # Case #1: File is specified
    if infile:
        try:
            input_source = open(infile,'r')
        except:
            print("File not found!")
            exit(130)
    # Case #2: College and date are specified
    elif college and datestr:
        try:
            if not dining.verify_name(college):
                print("Invalid college name!")
                exit (134)

            # Get them as 3 variables
            month,day,year = datestr.split('/')
            try :
                # Verify the date format
                datetime.datetime(int(year),int(month),int(day))
            except :
                print("Invalid date format!")
                exit(135)

            date = datestr

            # Check if it is cached
            if not nocache and os.path.exists(dining.get_path() + dining.get_filename(college, date)):
                input_source = open(dining.get_path() + dining.get_filename(college, date), 'r')
                using_cache=True
            else: # Otherwise create the request
                url = dining.get_url(college, datestr)
                input_source = requests.get(url).text
        except Exception as e:
            print(e)
            print("Invalid URL, college, or date")
            exit(132)
    # Case #3: College is specified (Assume today's date)
    elif college:
        try:
            if not dining.verify_name(college):
                print("Invalid college name!")
                exit(134)
                
            now_date = datetime.datetime.now().date()
            date = str(now_date.month) +"/" + str(now_date.day) + "/" + str(now_date.year)

            if not nocache and os.path.exists(dining.get_path() + dining.get_filename(college, date)):
                input_source = open(dining.get_path() + dining.get_filename(college, date), 'r')
                using_cache=True
            else:
                url = dining.get_url(college, date)
                input_source = requests.get(url).text
        except Exception as e:
            print("Invalid URL or college")
            print(e)
            exit(132)
    else:
        print("Incorrect arguments! Please specify either a college or an input file! See help for more information")
        exit(131)


    desired_meal = dining.get_current_meal()
    if meal:
        meal_id = dining.get_desired_meal(meal)
        if meal_id == -1:
            print("Invalid meal specified!")
            exit(139)
        else:
            desired_meal = meal_id

    if nocache or not (os.path.exists(dining.get_path() + dining.get_filename(college,date)) and os.path.isfile(dining.get_path() + dining.get_filename(college,date))):
        driver = dining.open_driver()
        cache_text = ""
        for x in range (0,4):
            try:
                # Get the parsed menu based on the starting index
                try:
                    meal_name, menu = dining.parse_menu(driver, college, dining.get_url(college,date), x)
                except Exception as e: print(e)
                
                # Start saving the text to cache
                cache_text += meal_name + '\n'
                for i in menu:
                    cache_text += i + '\n'
                cache_text += '\n'
                
                if x==0 and meal_name == "Lunch":
                    desired_meal -= 1
                elif x==0 and meal_name == "Dinner":
                    desired_meal -= 2
                elif x==0 and meal_name == "Late":
                    desired_meal -= 3
                
                # Print a seperator before the menu if it isn't our first time
                if all_meals:
                    if x != 0:
                        print()
                    # Print the menu
                    dining.print_menu(meal_name,menu)
                elif x == desired_meal:
                    dining.print_menu(meal_name,menu)
                # The next index has to add 3 and the length of the menu
                startIndex += len(menu) + 3
            except:
                # No more meals
                pass
        driver.quit()
        
        # Cache it
        if not infile:
            if using_cache:
                pass
            else:
                target_dt = dt.strptime(date, '%m/%d/%Y')
                target_day = target_dt.day
                today = target_dt.now().date()
                today_day = today.day
                if target_day < today_day or today_day + 7 < target_day:
                    pass # Bad date
                else:
                    dining.cache(dining.get_filename(college, date), cache_text)
    else: # This is using the cache
        with open(dining.get_path() + dining.get_filename(college,date), 'r') as cache_file:
            meals = list()
            meals.append(list())
            meals.append(list())
            meals.append(list())
            meals.append(list())
            current_list = 0
            for line in cache_file:
                if "Breakfast" in line:
                    current_list = 0
                    continue
                elif "Lunch" in line:
                    current_list = 1
                    continue
                elif "Dinner" in line:
                    current_list = 2
                    continue
                elif "Late" in line:
                    current_list = 3
                    continue
                elif line == "":
                    continue
                else:
                    pass
                meals[current_list].append(line)
            if all_meals:
                dining.print_menu("Breakfast", meals[0])
                print()
                dining.print_menu("Lunch", meals[1])
                print()
                dining.print_menu("Dinner", meals[2])
                print()
                dining.print_menu("Late", meals[3])
            elif desired_meal == 0:
                dining.print_menu("Breakfast", meals[0])
            elif desired_meal == 1:
                dining.print_menu("Lunch", meals[1])
            elif desired_meal == 2:
                dining.print_menu("Dinner", meals[2])
            else:
                dining.print_menu("Late", meals[3])
    
if __name__ == '__main__':
    description = 'Program to display UCSC dining hall options in all dining halls'
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("-f", "--file", help="use an input file")
    parser.add_argument("-c", "--college", help="specify college: \"cowell\", \"stevenson\", \"merrill\", \"crown\", \"kresge\", \"porter\", \"oakes\", \"rcc\", \"c9\", \"c10\"")
    parser.add_argument("-d", "--date", help="Specify the date in MM/DD/YYYY form")
    parser.add_argument('-a', '--all', dest='all_meals', help="Print the entire menu regardless of time and meal", action='store_true')
    parser.add_argument('-m', '--meal', help="Specify the meal you want")
    parser.add_argument('-i', '--invalidate-cache', dest='no_cache', help="Do not use the cache and force a pull from the internet", action='store_true')
    parser.set_defaults(all_meals=False)
    args = parser.parse_args()
    
    main(infile=args.file, college=args.college, datestr=args.date, nocache=args.no_cache, meal=args.meal, all_meals=args.all_meals)
    
