import requests
import pandas as pd
import json


API_KEY = "Write your API key here." # you can get API key from JCDecaux website by creating an account on it.
url = f"https://api.jcdecaux.com/vls/v1/stations?contract=Dublin&apiKey={API_KEY}"


response = requests.get(url)
data = response.json()


df = pd.DataFrame(data)


df.to_csv("bike_data.csv", index=False)
print("Data saved successfully as 'bike_data.csv'")


df.to_excel("bike_data.xlsx", index=False)
print("Data saved successfully as 'bike_data.xlsx'")
