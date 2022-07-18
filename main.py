from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import re
from tkinter import *
from statistics import mode
import plotly.express as px
from datetime import datetime
from collections import OrderedDict

class colours:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

semesterList = []
classList = []
count = 0

def getwebsite():
  global driver
  options = Options()
  #dont brint annoying usb error
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  #define driver
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  #get grades page on mE
  driver.get("https://me.eltham.edu.au/learning/grades")

  #waits until its on grades pages
  WebDriverWait(driver, 50).until(lambda driver: driver.find_elements(by=By.ID ,value='context-selector-semester'))
  #get all the semesters
  semesters = driver.find_element(By.ID, 'context-selector-semester')
  #delete new lines and add them to list
  for item in semesters.text.split("\n"):
    if "Semester" in item:
      semesterList.append(item.strip())

def getogradepage():
  semesterList.reverse()
  for semester in semesterList:
    #locates the form to be selected
    semesterform = driver.find_element(By.ID, 'context-selector-semester')
    #makes a variable that says what form its attached too
    selectedoption = Select(semesterform)
    #selects the semester
    selectedoption.select_by_visible_text(semester)

    #removes annoying stuff from the currenSemester
    currentSemester = re.sub("[\(\[].*?[\)\]]", "", semester)

    WebDriverWait(driver, 25).until(lambda driver: driver.find_elements(by=By.ID ,value='context-selector-subject'))

    #get all the semesters
    classes = driver.find_element(By.ID, 'context-selector-subject')
    #delete new lines and add them to list
    for item in classes.text.split("\n"):
      #remove annoying stuff
      item = item.strip()
      if "Select a subject" in item:
        continue
      if item == "":
        continue
      else:
        #locates the form to be selected
        classform = driver.find_element(By.ID, 'context-selector-subject')
        #makes a variable that says what form its attached too
        selectedoption = Select(classform)
        #selects the semester
        selectedoption.select_by_visible_text(item)
        #send the class into the get grades function
        getgrades(item, currentSemester)
        
    #reset the grades website, its a good trick   
    driver.get("https://me.eltham.edu.au/learning/grades")
  


def getgrades(Class, currentSemester):
  print(colours.BOLD + currentSemester + colours.END)
  print(colours.BOLD + Class + colours.END)

  #try to load if grades exist on the page
  try:
    WebDriverWait(driver, 5).until(lambda driver: driver.find_elements(by=By.XPATH ,value="//div[@class='small-12 card columns']/a/p"))
  except:
    WebDriverWait(driver, 5).until(lambda driver: driver.find_elements(by=By.XPATH ,value="//*[@id='report_content']/div/div/div/p"))
    
  #if there is a filter on the page and there is no items return
  try:
    element = assement.find_element(by=By.XPATH, value="//*[@id='report_content']/div/div/div/p")
    return
  except:
    pass

  #for assement in the class html page
  for assement in driver.find_elements(by=By.XPATH, value="//li[@class='assessment']"):
   
    #get the assement title
    assementTitle = assement.find_element(by=By.XPATH, value=".//div[@class='small-12 card columns']/a/p")

    duedatelementbox = assement.find_element(by=By.XPATH, value=".//span/time")
    dueDate = duedatelementbox.get_attribute('datetime')
      
    #get the grades (gradient is based on the percentage)
    for positiveNumber in range(0, 11):
      try:
        grade = assement.find_element(by=By.XPATH, value=f".//div[@class='grade gradient-{positiveNumber}-bg']/span")

        if grade.text == "":
          break
        else:
          print(assementTitle.text)
          print(grade.text)
          print(dueDate)
          organisedata(dueDate, currentSemester, assementTitle.text, grade.text, Class)
          break

      except:
        pass
      
everSingleGrade = []  

def organisedata(dueDate, semester, assement, grade, Class): 
  global everSingleGrade
  grade = re.sub("%", "", grade)

  if "Working Well Beyond" in grade:
    grade = 100

  elif "A+" in grade or "Very High" in grade:
    grade = 95
  elif grade == "A" or "High" in grade or "Working Beyond" in grade:
    grade =  85
  elif grade == "B+":
    grade = 77.5
  elif grade == "B":
    grade = 72.5

  elif grade == "C+" or "Consolidated" in grade:
    grade = 67.5
  elif grade == "C":
    grade = 62.5

  elif grade == "D+":
    grade = 57.5
  elif grade == "D":
    grade = 52.5

  elif grade == "E+" or "Developing" in grade:
    grade = 45
  elif grade == "E":
    grade = 35

  elif grade == "UG":
    grade = 15

  elif grade == "NG" or grade == "Not Completed" or "Not Yet" in grade:
    grade = 0
  
  elif "/" in grade:
    #remove spaces, idk just works better
    grade = re.sub(" ", "", grade)
    #partition the the file
    first, removed, second = grade.partition("/")
    
    if "." in first:
      if "." in second: 
        grade = float(first) / float(second)
      else:
        grade = float(first) / int(second)
    
    elif "." in second:
      grade = int(first) / float(second)

    else:
      grade = int(first) / int(second)

    #times by 100 to get a percentage
    grade = grade * 100
    #round to 2 decimals
    grade = round(grade, 1)   
  
  everSingleGrade.append(grade)
  print("grade was graphed as: " + str(grade))
  sendToOtherFunction(dueDate, grade, assement, semester, Class)

everysingle = {}
count = 0

def sendToOtherFunction(dueDate, grade, assement, semester, className):
  global count
  #counts 
  count = count + 1
  print(count)
  everysingle[count] = [dueDate, className, assement, grade, semester]

def showAverageGrade():
  totalpercent = 0
  for grade in everSingleGrade:
    if "." in str(grade):
     totalpercent = totalpercent + float(grade)
    else:
      totalpercent = totalpercent + int(grade)

  averageGrade = totalpercent / len(everSingleGrade)
  dataToBeShown = f"""
  Average Grade: {round(averageGrade,2)}%

  Assements completed: {len(everSingleGrade)}

  Most common Grade: {mode(everSingleGrade)}%
  """
  root = Tk()
  root.geometry("500x500")
  root.title("Averages")
  l = Label(root, text = dataToBeShown, anchor="center")
  l.config(font =("Arial", 24))
  l.place(x=230, y=250, anchor="center")
  root.mainloop()

     
def graphing():
  yaxis= []
  classes = []
  listOfTitles = []
  listOfDates = []
  listOfSemestersInOrder = []
  for itemnumber, listOfItems in everysingle.items():
    date = listOfItems[0]
    theclass = listOfItems[1]
    assementTitle = listOfItems[2]
    grade = listOfItems[3]
    semester = listOfItems[4]
    listOfSemestersInOrder.append(semester)

    
    listOfTitles.append(assementTitle)
    new = theclass.replace("'[]", "")
  
    newclass = re.sub("[\(\[].*[\)\]]", "", new)

    classes.append(str(newclass))
    listOfDates.append(str(date))
    
    if '.' in str(grade):
        yaxis.append(float(grade))
    else:
        yaxis.append(int(grade))
    
  count = 0
  xaxis = []

  for i in yaxis:
      count = count + 1
      xaxis.append(count)

  fig = px.scatter(x=xaxis, y=yaxis, color=classes, custom_data=[listOfTitles, classes, listOfSemestersInOrder], labels={"x": "Assement number", "y": "Grade (%)"})
  fig.update_yaxes(range = [-1,101])
  fig.update_layout(title_text="All time grades", title_font_size=30)
  fig.update_traces(marker=dict (size=9,), selector=dict(mode='markers'))
  fig.update_traces(hovertemplate = "<b>%{customdata[0]}</b> <br>Grade: %{y} </br>Subject: %{customdata[1]} </br>Semester: %{customdata[2]}")

  fig.show()
 
if __name__ == '__main__':
  getwebsite()
  getogradepage()
  everysingle = OrderedDict(sorted(everysingle.items(), key = lambda date:datetime.strptime(date[1][0].strip(), '%Y-%m-%dT%H:%M:%S%z'), reverse=False))
  print(everysingle)
  showAverageGrade()
  graphing()
