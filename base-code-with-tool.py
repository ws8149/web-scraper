import multiprocessing
import timeit
import csv
import re
import time

import requests
from selenium import webdriver
from bs4 import BeautifulSoup, Tag

# Setup Chrome display
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

# List of keywords for level
level_key = {'FUG': ['Foundation'], 'VOC': ['Cert'], 'DIP': ['Diploma'], 'ADIP': ['Advance'],
             'UG': ['Bachelor', 'Baccalaureate', 'Degree', 'BA', 'BSc', 'Baccalauréat-ès-Arts', 'Baccalauréat'], 'GPG': ['Graduate Diploma', 'GDip', 'Post Baccalaureate Diploma'], 'GPC': ['Graduate Cert'],
             'PG': ['Master', 'Postgrad', "Master's"],  'DPG': ['Doctor', 'PhD'], 'SHORT COURSES': ['Short', 'Course'], 'SEMINAR': ['Seminar'], 'PRODEV': ['Tailor'], 'CONF': ['Conference'], 'HONS': ['Honours']}



def clean(stringToClean):
    stringToClean = ' '.join(stringToClean.split())
    return re.sub(r'[^\x00-\x7f]', r' ', stringToClean)



def convertNum(Text):
    return Text.replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4').replace('five', '5').replace('six', '6').replace('seven', '7').replace('eight', '8').replace('nine', '9')


def convertDuration(duration):
    duration = duration.lower()
    duration = convertNum(duration)
    numbers = re.findall(r'\d+(?:\.\d+)?', duration)

    dur_type_list = []
    for word in duration.split():
        if 'mester' in word.lower() or 'term' in word.lower() or 'hour' in word.lower() or 'day' in word.lower() or 'week' in word.lower() or 'month' in word.lower() or 'year' in word.lower() or 'credit' in word.lower():
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
            elif 'credit' in dur:
                return str  (number), 'Credit Hours'
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

def collect_data(process_num, course_url_list, course_name_list, course_dur_list):
    # This will get the keywords from faculty file and put it into a dictionary
    with open('C:/Users/veye/Dropbox/Scrapping/Others/faculty.csv', 'rt', encoding='utf-8') as List:  # Can use the faculty file from the Dropbox also.
        reader = csv.reader(List)
        mydict = {rows[0]: rows[1] for rows in reader}

    # This part will scrape the page
    with open('C:/Scrape/your_uni_folder/ExtractedData_' + '_all' + '.csv', 'at', newline='', encoding='utf-8-sig') as website:
        writer = csv.writer(website)

        while True:
            num_loop = 0
            while num_loop < len(course_url_list):

                req = requests.get(course_url_list[num_loop])
                soup = BeautifulSoup(req.content, 'lxml')

                # details['Course Name', 'Level', 'Faculty', 'Duration', 'Duration Type', 'URL', 'Description', 'Keywords', 'ScrapeAll']
                details = ['', '', '', '', '', '', '', '', '', '']

                ##

                # Course name
                if 'null' in course_name_list[num_loop]:
                    ""
                else:
                    details[0] = course_name_list[num_loop]


                #-------------------------------  change code here ---------------------------------------------

                # Duration Text
                durationText = soup.find('div', {'class': 'someclassnameyouhavetofind'}).text




                # Description
                descText = soup.find('div',{'class': 'someclassnameyouhavetofind'}).text
                details[6] = clean(descText)



                #--------------- you don't have to change anything past here unless you really need to --------------


                # Duration and Duration Type
                # this returns a pair duration (int), durationtype (string)
                durationPair = convertDuration(durationText)
                details[3] = durationPair[0]
                details[4] = durationPair[1]

                # Both the code for levels and faculty can be changed to suit the website that you are doing.
                # Levels
                word = details[0]
                lock = 0
                for level, key in level_key.items():
                    for each in key:
                        for wd in word.split():
                            if each.lower() == wd.lower():  # Testing the equal, might change back to in
                                details[1] = level
                                lock = 1
                                break
                        if lock == 1:
                            break
                    if lock == 1:
                        break

                # Faculty
                loop_must_break = False
                for a in details[0].split():
                    for fac, key in mydict.items():
                        for each in key.split(','):
                            if each.replace("'", '').title() in a:
                                print("\t\t\t" + each + '  in  ' + details[0] + ' from ' + course_url_list[num_loop])
                                details[2] = fac
                                loop_must_break = True
                                break
                        if loop_must_break:
                            break
                    if loop_must_break:
                        break

                # URL
                details[5] = req.url

                # Scrape All
                [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
                visible_text = repr(soup.get_text().replace(r'\\n', ' ').replace('\n', '').replace('\\', '').replace(', ', ''))
                visible_text = re.sub(r'[^\x00-\x7f]', r' ', visible_text)
                visible_text = ' '.join(visible_text.split())

                details[7] = str(repr(visible_text))

                writer.writerow(details)
                print(details)
                print("Page " + str(num_loop) + '/' + str(len(course_url_list)) + " from " + '_all')
                time.sleep(3)
                num_loop += 1
            print("\n" + str(len(course_url_list)) + " in the queue of " + '_all')

            print("\n" + '_all' + " has exited the loop")
            break



def main():
    start = timeit.default_timer()

    with open('C:/Scrape/your_uni_folder/ExtractedData_' + '.csv', 'wt', encoding="utf-8",
              newline='') as website:
        writer = csv.writer(website)
        writer.writerow(
            ['Course Name', 'Level', 'Faculty', 'Duration', 'Duration Type', 'URL', 'Description', 'ALLTXT'])
    big_url_list = []  # Stores all the URLs in 200s
    big_name_list = []  # Stores all the names in 200s
    big_dur_list = []  # Stores all the desc

    course_url_list = []  # This list will store all the URL from the file
    course_name_list = []  # This will store all the course name from the file
    course_dur_list = []  # This will store all the desc from the file

    with open('C:/Scrape/your_uni_folder/uni_name' + '.csv', 'rt', encoding="utf-8", newline='') as course_link:
        reader = csv.reader(course_link)
        data_row = []
        next(reader)
        for row in reader:
            data_row.append(row)

        last_row = data_row[-1]
        # print(last_row[1])

    with open('C:/Scrape/your_uni_folder/uni_name' + '.csv', 'rt', encoding="utf-8", newline='') as course_link:
        reader = csv.reader(course_link)
        count = 1
        n = 0  # count links
        next(reader)

        # -------------------------------  change code here ---------------------------------------------
        #the index here refers to the column index of the web scraper extension output csv

        dname = 2   # The index of the item
        durl = 5  # The index of the item
        ddur = 3  # The index of the item

        # ----------------------------------------------------------------------------------------------

        # Allows the links to run 50 per process
        for row in reader:
            tmp_url = []
            tmp_name = []
            tmp_dur = []
            if n == 49 or last_row[0] in row[0]:
                course_name_list.append(row[dname])
                course_url_list.append(row[durl])
                course_dur_list.append(row[ddur])
                count += 1

                for item in course_url_list:
                    tmp_url.append(item)
                big_url_list.append(tmp_url)
                for item in course_name_list:
                    tmp_name.append(item)
                big_name_list.append(tmp_name)
                for item in course_dur_list:
                    tmp_dur.append(item)
                big_dur_list.append(tmp_dur)

                course_name_list.clear()
                course_url_list.clear()
                course_dur_list.clear()
                n = 0
            else:
                course_name_list.append(row[dname])
                course_url_list.append(row[durl])
                course_dur_list.append(row[ddur])
                count += 1
                n += 1

    num_process = 30  # Number of processes running at one time. Change this to 1 for testing.
    all_process = len(big_url_list)  # Total number of processes that should run. Change this according to uni. Change this to 1 for testing.
    num_finish_process = 0  # Count for finished process
    count_process = 0  # Count number of processes running
    process_num = 0  # This is for the course type in collect_data function
    process = []
    values = []

    def create_process(process_num, count_process):  # Function to create and start process
        process_num = process_num + 1  # This is for the course type in collect_data function
        new_process = multiprocessing.Process(target=collect_data, args=(
        process_num, big_url_list.pop(), big_name_list.pop(), big_dur_list.pop()))
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