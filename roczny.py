import plotly.express as px
import pyodbc 
import pandas as pd
  
def getDataFromDatabase():
    connection = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-27L34L8;'
                          'Database=Treningi;'
                          'Trusted_Connection=yes;')   
    cursor = connection.cursor()
    cursor.execute('SELECT YEAR(w.startTime) AS "rok", a.name AS "sport", SUM(w.distance) "dystans" FROM workouts w INNER JOIN activityTypes a ON w.activityTypeID = a.activityTypeID GROUP BY YEAR(w.startTime), a.name ORDER BY YEAR(w.startTime), a.name')
    data = cursor.fetchall()
    cursor.close()
    
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT a.name "sport" FROM workouts w INNER JOIN activityTypes a ON w.activityTypeID = a.activityTypeID')
    sportsRow = cursor.fetchall()
    sports = []
    for sport in sportsRow:
        sports.append(sport[0])
    cursor.close()
    connection.close()
    return data, sports
  
def getSportAndYearDistance(data, sport, year):
    distance = 0
    for d in data:
        if(d[0] == year and d[1] == sport):
            distance = round(d[2], 3)
            break
    return distance  
    
def prepareData(data, sports):
    minYear = data[0][0]
    maxYear = data[len(data)-1][0]
    print("----------------------------")
    print(minYear, maxYear)
    labels = list(range(minYear, maxYear+1, 1))
    
    preparedData = {}
    for s in sports:
        for y in labels:
            preparedData[(s, y)] = getSportAndYearDistance(data, s, y) 
    
    dataForDF = {
        "Rok": labels
    } 
    
    distanceValues = list(preparedData.values())
    for i in range(len(sports)):
        print(sports[i], distanceValues[i*len(labels) : (i+1)*len(labels)]) 
        dataForDF[sports[i]] = distanceValues[i*len(labels) : (i+1)*len(labels)]
         
    df = pd.DataFrame(dataForDF)
    print(df) 

    return labels, df
   
def drawChart(sports, df):
    fig = px.bar(df, x="Rok", y=sports, title="Dystans w poszczególnych latach")  
    fig.write_html('roczny.html')

data, sports = getDataFromDatabase()
labels, df = prepareData(data, sports)  
drawChart(sports, df)       

