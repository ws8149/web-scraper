import multiprocessing
import timeit
import csv
import re
import time
import sys
import traceback
from collections import deque

import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

with open('C:/Scrape/monash/UniqueLinkList_monash.csv', 'wt') as Linklist:
    Linklist.close()

# Setup Chrome display
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
ua = UserAgent()

# change code here
Url = deque(["https://www.monash.edu/study/courses/find-a-course?collection=study-monash-courses-meta&f.Tabs%7CcourseTab=Undergraduate&f.InterestAreas%7CcourseInterestAreas="])



# List of Course Name Keywords for course names
keywords = ['cert', 'diploma', 'program', 'course', 'master', 'grad', 'doctor', 'degree', 'bachelor', 'ship', 'and']

# List of keywords for level
level_key = {'FUG': ['Foundation'], 'VOC': ['Cert', 'CMT', 'CAS', 'Certificate', 'Credential', 'Credentials'],
             'DIP': ['Diploma'], 'ADIP': ['Advance'],
             'UG': [ 'B.S.', 'B.A.', 'B.S.B.A.', 'BS', 'Bachelor', 'B.Trad.', 'BGInS', 'BAcc', 'BAFM', 'BAdmin', 'BAS', 'BAA', 'BASc', 'BASc/BEd',
                    'BArchSc', 'BAS', 'BA', 'BAS', 'BSN', 'BASc/BEd', 'BASc', 'BA/BComm', 'BA/BEd', 'BA/BEd/Dip', 'BA/LLB',
                    'BA/MA', 'BBRM', 'BBA', 'BEd', 'BCD', 'BBA/BA', 'BBA/BCS', 'BBA/BEd', 'BBA/BMath', 'BBA/BSc', 'BBE', 'BBTM',
                    'BCogSc', 'BComm', 'BCom', 'BCoMS', 'BCoSc', 'BMT', 'BCS', 'BComp', 'BCmp', 'BCFM', 'BDes', 'BDEM',
                    'BEcon', 'BEng', 'BEng&Mgt', 'BEngSoc', 'BAM', 'BESc', 'BEngTech', 'BEM', 'BESc', 'BESc/BEd', 'BES',
                    'BES/BEd', 'BFAA', 'BFA,BFA/BEd', 'BFS', 'BGBDA', 'BHP', 'BHSc', 'BHSc', 'BHS', 'BHS/BEd',
                    'BHum', 'BHK', 'BHRM', 'BID', 'BINF', 'BIT', 'BID', 'BIB', 'BJ', 'BJour', 'BJourn', 'BJHum',
                    'BKin', 'BK/BEd', 'BKI', 'BLA', 'BMOS', 'BMath', 'BMath/BEd', 'BMPD', 'BMRSc', 'BMSc', 'BMus',
                    'MusBac', 'BMusA', 'BMus/BEd', 'BMuth', 'BOR', 'BOR/BA', 'BOR/BEd', 'BOR/BSc', 'BPHE', 'BPhEd',
                    'BPHE/BEd', 'BPA', 'BPAPM', 'BPH', 'BRLS', 'BSc', 'BSc&Mgt', 'BSc/BASc', 'BSc/BComm', 'BSc/BEd',
                    'BSc(Eng)', 'BScFS', 'BScF', 'BSc(Kin)', 'BScN', 'BSocSc', 'BSW', 'BSE', 'BSM', 'BTech', 'BTh',
                    'BURPI', 'iBA,iBA/BEd', 'iBBA', 'iBSc', 'iBSc/BEd'], 'GPG': ['Graduate Diploma', 'GDip', 'Post Baccalaureate Diploma'], 'GPC': ['Graduate Cert'],
                    'PG': ['(Ed.S.)', 'Master', 'Postgrad', 'MPhil', 'MCD', 'MSc', 'LLM', 'MA', 'MSW', "Master's", 'Masters' ],
                    'DPG': ['Doctor', 'PhD', 'Doctorate/PhD'],
                    'SHORT COURSES': ['Short', 'Course', 'Programme'], 'SEMINAR': ['Seminar'],
                    'PRODEV': ['Tailor'], 'CONF': ['Conference'],
                    'HONS': ['Honours','Honors'],
                    'MINOR': ['Minor'],
                    'PROGRAM' : ['Program','Programs'],
                    'ASSOCIATE' : ['Associate']
             }

#      Day, Week, Month, Year
CLA = [24, 168, 720, 8760]  # Hours


def get_text_with_br(tag, result=''):
    for x in tag.contents:
        if isinstance(x, Tag):  # check if content is a tag
            if x.name == 'br':  # if tag is <br> append it as string
                result += str(x)
            else:  # for any other tag, recurse
                result = get_text_with_br(x, result)
        else:  # if content is NavigableString (string), append
            result += x

    return result

class Methods:
    # Check if the variable datatype is None
    def CheckNone(link):
        if link != None:
            return True
        else:
            return False

    # Check if the passed string contains http or https
    def HttpCheck(link):
        if Methods.CheckNone(link):
            if ('https://' in link) or ('http://' in link):
                return True
            else:
                return False
        else:
            return False

    # Check if link is Unique
    def Unique(link):
        with open('C:/Scrape/monash/UniqueLinkList_monash.csv', 'rt', encoding='utf-8') as Linklist:
            reader = csv.reader(Linklist)
            for url in reader:
                if Methods.CheckNone(link) & Methods.CheckNone(url):
                    if link == url:
                        Linklist.close()
                        return False
                else:
                    Linklist.close()
                    return False
            return True

    def Check_CN(name):
        for a in keywords:
            if a in name:
                return False
        return True

def clean(stringToClean):
    stringToClean = ' '.join(stringToClean.split())
    return re.sub(r'[^\x00-\x7f]', r' ', stringToClean)

def convertLeast(x, y):
    return round(x * CLA[y - 1])

#takes in a string describing the duration and returns a pair of duration and duration type
def convertDuration(duration):
    duration = duration.lower()
    duration = convertNum(duration)
    numbers = re.findall(r'\d+(?:\.\d+)?', duration)

    dur_type_list = []
    for word in duration.split():
        if 'mester' in word.lower() or 'term' in word.lower() or 'hour' in word.lower() or 'day' in word.lower() or 'week' in word.lower() or 'month' in word.lower() or 'year' in word.lower():
            dur_type_list.append(word)
    # print(dur_type_list)

    nums = []
    for number in numbers:
        if number != '':
            nums.append(number)
    # print(nums)

    for number in nums:
        for dur in dur_type_list:
            if 'year' in dur:
                if '.' in number:
                    if re.findall(r'\d+', duration)[1] != 0:
                        return convertDuration(str(round(float(number) * 12)) + ' month')
                    return int(re.findall(r'\d+', duration)[0]), 'Years'
                else:
                    return int(number), 'Years'
            elif 'month' in dur:
                if '.' in number:
                    if re.findall(r'\d+', duration)[0] < 7:
                        return convertDuration(str(int(float(number) * 4)) + ' week')
                elif int(number) % 12 == 0:
                    return int(int(number) / 12), 'Years'
                else:
                    return int(round(float(number))), 'Months'
            elif 'week' in dur:
                return round(int(number)), ' Weeks'
            elif 'hour' in dur:
                return int(number), 'Hours'
            elif 'semester' in dur:
                return convertDuration(str(int(number) * 6) + 'month')
            elif 'trimester' in dur:
                return convertDuration(str(int(number) * 3) + 'month')
            elif 'term' in dur:
                return convertDuration(str(int(number) * 6) + 'month')
            elif 'day' in dur:
                if '.' in number:
                    for jk in re.findall(r'\d+', duration):
                        if int(jk) > 1:
                            return convertDuration(str(int(float(number) * 24)) + 'hour')
                else:
                    return int(number), 'Days'
            else:
                return 'WRONG DATA'

def convertNum(Text):
    return Text.replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4').replace('five', '5').replace('six', '6').replace('seven', '7').replace('eight', '8').replace('nine', '9')

def getAllTxt(soup):
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    visible_text = repr(
        soup.get_text().replace(r'\\n', ' ').replace('\n', '').replace('\\', '').replace(', ', ''))
    visible_text = re.sub(r'[^\x00-\x7f]', r' ', visible_text)
    visible_text = ' '.join(visible_text.split())
    return str(repr(visible_text))

def getFacultyFromTitle(title,mydict):
    loop_must_break = False
    word = title.lower()

    if " in " in word:
        word = word.split(" in ", 1)[1]


    for a in word.split():
        for fac, key in mydict.items():
            for each in key.split(','):
                # print(each.replace("'", '') + "==" + a)
                if each.replace("'", '') in a:
                    return fac
            if loop_must_break:
                break
        if loop_must_break:
            break

    return ""

def getLevelFromTitle(title):
    # Levels
    word = title.replace(':','')
    lock = 0
    for level, key in level_key.items():
        for each in key:
            for wd in word.split():
                if each.lower() == wd.lower():  # Testing the equal, might change back to in
                    return level
                    lock = 1
                    break
            if lock == 1:
                break
        if lock == 1:
            break
    return ""


def collect_links(link):
    # Only change the executable_path to your path. Leave the chrome_options.
    user = ua.random
    print(user)
    options.add_argument(f'user-agent={user}')

    course_url_list = []
    # Get all the course links from the page and place it inside the UniqueLinkList.
    num = 0

    ##Getting links
    container = []

    req = requests.get(link)
    soup = BeautifulSoup(req.content, 'lxml')
    time.sleep(2)

    #----------------------------- change code here -------------------------------------------------

    pageSoupList = soup.find_all('li', {'class': 'search-tabs__item'})
    pageSoupList.pop()

    for p in pageSoupList:
        req = requests.get("https://www.monash.edu/study/courses/find-a-course" + p.a.get('href'))
        soup = BeautifulSoup(req.content, 'lxml')

        courseLinkSoupList = soup.find_all('h2', {'class': 'box-featured__heading'})
        for l in courseLinkSoupList:
            container.append(l.a.get('href'))

    #--------------------------------------------------------------------------------------

    for course_link in container:
        if Methods.HttpCheck(course_link) & Methods.Unique(course_link.split('\n')):
            with open('C:/Scrape/monash/UniqueLinkList_monash_all.csv', 'at', encoding='utf-8', newline='') as Linklist:
                writer = csv.writer(Linklist)
                u = (str(course_link).split('\n'))
                writer.writerow(u)
            print(course_link)
            Linklist.close()
            course_url_list.append(course_link)
            num += 1

    print("================================\nAll " + str(num) + " the links have been collected")

def collect_data(process_num,course_url_list):


    # This will get the keywords from faculty file and put it into a dictionary
    with open('C:/Scrape/faculty.csv', 'rt', encoding='utf-8') as List:
        reader = csv.reader(List)
        mydict = {rows[0]: rows[1] for rows in reader}


    ##loop through links to get all content
    with open('C:/Scrape/monash/monash_ExtractedData_all.csv', 'at', encoding="utf-8", newline='') as website:
        writer = csv.writer(website)


        count = 0
        for element in course_url_list:
            req = requests.get(element)
            soup = BeautifulSoup(req.content, 'lxml')

            #               0           1          2         3            4             5          6            7            8
            # details['Course Name', 'Level', 'Faculty', 'Duration', 'Duration Type', 'URL', 'Description', 'Keywords', 'ScrapeAll']
            details = ['', '', '', '', '', '', '', '', '', '']

            print(str(count) + "/" + str(len(course_url_list)) + " Scraping from.." + element)

            title = ''
            desc = ''
            durationText = ''
            durationType = ''
            duration = ''

            # ----------------------------- change code here -------------------------------------------------

            #get title
            try:
                title = soup.find('div',{'class': 'grid-col-sm-12 grid-col-md-12-12 page-header-courses'}).text

            except:
                print("\terror getting title, please double check")

            # #get duration
            try:
                durationText = soup.find('table',{'class': 'course-page__table-basic'}).text
            except:
                print("\terror getting durationText, please double check")

            try:
                duration = str(convertDuration(durationText)[0])
                durationType = str(convertDuration(durationText)[1])
            except:
                print("\terror converting duration, please double check")

            #get desc

            try:
                desc = soup.find('div',{'class': 'course-page__summary-text'}).text
            except:
                print("\terror getting description, please double check")

            #---------------------------------------------------------------------------------------

            details[0] = clean(title)
            details[1] = getLevelFromTitle(details[0])
            details[2] = getFacultyFromTitle(details[0], mydict)
            details[3] = duration
            details[4] = durationType
            details[5] = str(req.url)
            details[6] = clean(desc)
            details[7] = getAllTxt(soup)



            print('\t Title: ' + details[0])
            print('\t Duration: ' + details[3])
            print('\t Duration Type: ' + details[4])
            print('\t Description: ' + details[6] )
            print('\t Faculty: ' + details[2])
            print('\t Level: ' + details[1])

            if details[2]:
                writer.writerow(details)
            else:
                print("\t error getting faculty, skipping course, please double check")
            count += 1
        # driver.quit()
        exit


def main():
    start = timeit.default_timer()

    # Create the UniqueLinkList file.
    with open('C:/Scrape/monash/UniqueLinkList_monash_all.csv', 'wt') as Linklist:
        Linklist.close()

    collect_links(Url.pop())  # Call this to collect the links first.

    # Create an output file
    with open('C:/Scrape/monash/monash_ExtractedData_all.csv', 'wt', encoding='utf-8-sig', newline='') as website:
        writer = csv.writer(website)
        writer.writerow(
            ['Course Name', 'Level', 'Faculty', 'Duration', 'Duration Type', 'URL', 'Description', 'ALLTXT'])

    # Get the last row from UniqueLinkList
    with open('C:/Scrape/monash/UniqueLinkList_monash_all.csv', 'rt', encoding="utf-8") as course_link:
        reader = csv.reader(course_link)
        data_row = []
        next(reader)
        for row in reader:
            data_row.append(row)

        last_row = data_row[-1]

    big_url_list = []  # This list will store the course_url_list

    course_url_list = []  # This list will store the number of URL that you set.

    # This will read the links from UniqueLinkList
    with open('C:/Scrape/monash/UniqueLinkList_monash_all.csv', 'rt',
              encoding="utf-8") as course_link:  # Change the directory.
        reader = csv.reader(course_link)
        count = 1
        n = 0  # count links

        durl = 0  # The index of the item

        for row in reader:
            tmp_url = []
            if n == 49 or last_row[0] in row[0]:  # The number is how much link you want for one process.
                course_url_list.append(row[durl])
                count += 1

                for item in course_url_list:
                    tmp_url.append(item)
                big_url_list.append(tmp_url)

                course_url_list.clear()
                n = 0
            else:
                course_url_list.append(row[durl])
                count += 1
                n += 1

    print('The total number of  process is ' + str(len(big_url_list)))

    num_process = 4  # Number of processes running at one time. Change this to 1 for testing.
    all_process = len(
        big_url_list)  # Total number of processes that should run. Change this according to uni. Change this to 1 for testing.
    num_finish_process = 0  # Count for finished process
    count_process = 0  # Count number of processes running
    process_num = 0  # This is for the course type in collect_data function
    process = []
    values = []

    def create_process(process_num, count_process):  # Function to create and start process
        process_num = process_num + 1  # This is for the course type in collect_data function
        new_process = multiprocessing.Process(target=collect_data, args=(process_num, big_url_list.pop()))
        process.append(new_process)
        new_process.start()
        count_process += 1

        return [process_num, count_process]

    def start_process():  # Function that will call the create process function.
        nonlocal process_num, count_process, all_process
        nonlocal values

        values = create_process(process_num, count_process)

        process_num = values[0]
        count_process = values[1]

    while True:
        if count_process < num_process and process_num < all_process:  # Check if there is still processes left to be run, create new process if needed
            start_process()
            print("Starting process")

        for proc in process:  # Loop that will check for status of process
            proc.join(timeout=0)
            if not proc.is_alive():
                process.remove(proc)  # Remove the finished process from the list
                print("Process Ended!")
                num_finish_process += 1
                print('Completed Processes:')
                print(num_finish_process)
                remain_proc = int(all_process) - int(num_finish_process)
                print('Remaining Processes:')
                print(remain_proc)
                count_process -= 1
                break

        if count_process == 0 and num_finish_process == all_process:
            print("All is done" + "\t\tTotal finished process " + str(num_finish_process))
            break

    stop = timeit.default_timer()
    time_sec = stop - start
    time_min = int(time_sec / 60)
    time_hour = int(time_min / 60)

    time_run = str(format(time_hour, "02.0f")) + ':' + str(
        format((time_min - time_hour * 60), "02.0f") + ':' + str(format(time_sec - (time_min * 60), "^-05.1f")))
    print("This code has completed running in: " + time_run)


if __name__ == '__main__':
    main()

