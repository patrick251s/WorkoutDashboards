import plotly.express as px
import pyodbc 
import pandas as pd
  
def getDataFromDatabase():
    connection = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-27L34L8;'
                          'Database=Treningi;'
                          'Trusted_Connection=yes;')   
    cursor = connection.cursor()
    cursor.execute('SELECT YEAR(w.startTime), MONTH(w.startTime), a.name, SUM(w.distance) FROM workouts w INNER JOIN activityTypes a ON w.activityTypeID = a.activityTypeID GROUP BY YEAR(w.startTime), MONTH(w.startTime), a.name ORDER BY 1,2,3')
    data = cursor.fetchall()
    cursor.close()
    
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT a.name FROM workouts w INNER JOIN activityTypes a ON w.activityTypeID = a.activityTypeID ORDER BY 1')
    sportsRow = cursor.fetchall()
    sports = []
    for sport in sportsRow:
        sports.append(sport[0])
    cursor.close()
    connection.close()
    return data, sports
   
def getLabels(minYear, minMonth, maxYear, maxMonth):
    labels = []
    for y in range(minYear, maxYear+1):
        if(y == minYear):
            for m in range(minMonth, 13):
                labels.append(str(y)+"-"+str(m))
        elif(y == maxYear):
            for m in range(1, maxMonth+1):
                labels.append(str(y)+"-"+str(m))
        else:
            for m in range(1, 13):
                labels.append(str(y)+"-"+str(m))
    return labels

def getDistanceFromMonth(data, date, sport):
    distance = 0
    adding = 0
    
    #yyyy-m
    if(len(date) == 6):
        adding = 1  

    for d in data:
        if(d[0] == int(date[0:4]) and d[1] == int(date[5:7-adding]) and d[2] == sport):
            distance = round(d[3], 3)
            break
    return distance

def prepareData(data, sports):
    minYear = data[0][0]
    minMonth = data[0][1]
    maxYear = data[len(data)-1][0]
    maxMonth = data[len(data)-1][1]
    labels = getLabels(minYear, minMonth, maxYear, maxMonth)
    
    preparedData = {}
    for s in sports:
        for labelDate in labels:
            preparedData[(s, labelDate)] = getDistanceFromMonth(data, labelDate, s)
    
    dataForDF = {
        "Okres": labels
    } 
    
    distanceValues = list(preparedData.values())
    for i in range(len(sports)):
        dataForDF[sports[i]] = distanceValues[i*len(labels) : (i+1)*len(labels)]
        
    df = pd.DataFrame(dataForDF)
    print(df)
    
    return df
   
def drawChart(sports, df):
    fig = px.bar(df, x="Okres", y=sports, title="Dystans w poszczególnych miesiącach")  
    fig.write_html('miesieczny_szczegolowy.html')

data, sports = getDataFromDatabase() 
df = prepareData(data, sports)
drawChart(sports, df)      
