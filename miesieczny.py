import plotly.express as px
import pyodbc 
import pandas as pd
  
def getDataFromDatabase():
    connection = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-27L34L8;'
                          'Database=Treningi;'
                          'Trusted_Connection=yes;')   
    cursor = connection.cursor()
    cursor.execute('SELECT MONTH(w.startTime), a.name, SUM(w.distance) FROM workouts w INNER JOIN activityTypes a ON w.activityTypeID = a.activityTypeID GROUP BY MONTH(w.startTime), a.name ORDER BY 2')
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

def getDistanceFromMonth(data, month, sport):
    distance = 0
    for d in data:
        if(d[0] == month and d[1] == sport):
            distance = round(d[2], 3)
            break
    return distance

def prepareData(data, sports):
    months = list(range(1, 13))
    monthsName = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
    preparedData = {}
    for s in sports:
        for m in months:
            preparedData[(s, m)] = getDistanceFromMonth(data, m, s)
    
    dataForDF = {
        "Miesiąc": monthsName
    } 
    
    distanceValues = list(preparedData.values())
    for i in range(len(sports)):
        dataForDF[sports[i]] = distanceValues[i*len(months) : (i+1)*len(months)]
        
    df = pd.DataFrame(dataForDF)
    print(df) 
    
    return df
    
def drawChart(sports, df):
    fig = px.bar(df, x="Miesiąc", y=sports, title="Dystans w poszczególnych miesiącach")  
    fig.write_html('miesieczny.html')
      
data, sports = getDataFromDatabase()
df = prepareData(data, sports)
drawChart(sports, df)
