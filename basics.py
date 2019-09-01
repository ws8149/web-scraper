Requests
req = requests.get(page)
soup = BeautifulSoup(req.content, 'lxml')

Check size
str(len(listname))

Find all in one level
soup.find_all('li', recursive=False)

Find next tag
dtSoup.find_next_sibling('dd')
eg:
<dt>
<dd>

pop
['abc',dec','cas']

pop() removes and returns 'cas'
pop(0) removes and returns 'abc'

Empty string
if not foo

Notempty string
if foo

Remove dupe
container = set(container)

Translator
from googletrans import Translator
translator = Translator()

Continue from timeout
    with open('C:/Scrape/nku/UniqueLinkList_nku.csv', 'r') as f:
        reader = csv.reader(f)
        csvLinkList = list(reader)

    for sublist in csvLinkList:
        for item in sublist:
            course_url_list.append(item)
    print(course_url_list)

Remember to stop creation of new link list

Filter out objects in a list using a list
s1 = ['a','b','c','d']
s2 = ['a','b']

#s2 contains the things i dont want
def is_equal(x,s2):
  if x not in s2:
    return True
  else:
    return False

# lambda x refers to the object within s1
# it works just like the the the "x" in a
# "for x in s1 loop"
f = filter(lambda x: is_equal(x,s2), s1)

print(list(f))

Selenium js click
element = driver.find...
driver.execute_script("arguments[0].click();", element)

UTF get
.get_text()

Good foundations
standard - monash
ul li compressor - sonoma
pagination - hanze
time difference finder - ihe