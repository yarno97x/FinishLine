import requests, json, os, joblib
from bs4 import BeautifulSoup
import pandas as pd, numpy as np
from datetime import date

with open('data/links.json', 'r', encoding='utf-8') as f:
    LINKS = json.load(f)
print("Updating...")
class Scraper:
  def __init__(self):
    self.qualifying_2025 = pd.DataFrame(columns=["TrackId", "Code", "Team", "Q1", "Q2", "Q3", "Grid", "Year"])
    self.races_2025 = pd.DataFrame(columns=["TrackId", "Code", "Position", "FastestLap"])
    self.today = int(date.today().strftime("%j"))

    if os.path.exists("metadata.json") and os.path.getsize("metadata.json") > 0:
       with open("data/metadata.json", "r", encoding="utf-8") as f:
         self.last_scraped = json.load(f)
    else:
       self.last_scraped = 0

  def extract_qualifying(self):
      for race in LINKS.values():
          if race['day'] > self.today or race['day'] <= self.last_scraped:
             break
          path = race["url"] + "/qualifying"
          soup = BeautifulSoup(requests.get(path).text, "lxml")
          table = soup.find("tbody")
          rows = table.find_all("tr")

          for row in rows:
            grid, _, name, team, q1, q2, q3, _ = [val.text for val in row.find_all("td")]
            name, code = name[:-3], name[-3:]
            self.qualifying_2025.loc[len(self.qualifying_2025)] = [race['id'], code, team, q1, q2, q3, grid, 2025]

    
  def extract_races(self):
      for race in LINKS.values():
          if race['day'] > self.today or race['day'] <= self.last_scraped:
             break
          path = race["url"] + "/race-result"
          soup = BeautifulSoup(requests.get(path).text, "lxml")
          table = soup.find("tbody")
          rows = table.find_all("tr")

          for row in rows:
            position, _, name, _, _, _, _= [val.text for val in row.find_all("td")]
            code = name[-3:]
            self.races_2025.loc[len(self.races_2025)] = [int(race['id']), code, position, "_"]

  def extract_fastest_laps(self):
      for race in LINKS.values():
          if race['day'] > self.today or race['day'] <= self.last_scraped:
             break
          path = race["url"] + "/fastest-laps"
          soup = BeautifulSoup(requests.get(path).text, "lxml")
          table = soup.find("tbody")
          rows = table.find_all("tr")
          for row in rows:
            row_vals = [val.text for val in row.find_all("td")]
            code = row_vals[2][-3:]
            self.races_2025.loc[self.races_2025.Code == code, "FastestLap"] = row_vals[-2]

  def scrape(self):
     self.extract_qualifying()
     self.extract_races()
     self.extract_fastest_laps()
     self.last_scraped = self.today
  def merge_current(self):
     return pd.merge(self.qualifying_2025, self.races_2025, how="right", on=["TrackId", "Code"])
  
  def load(self, df):
     self.old_df = df

  def save(self):
     pd.concat([self.old_df, self.merge_current()]).to_csv("data/season_2025.csv", index=False)
     with open("data/metadata.json", "w", encoding="utf-8") as f:
        json.dump(self.last_scraped, f)

  def check(self):
      try:
         df = pd.read_csv("data/season_2025.csv")
      except FileNotFoundError:
         df = pd.DataFrame()
         
      self.load(df)
      self.scrape()
      self.save()

def remove_2025_season():
    if os.path.exists("data/metadata.json"):
        os.remove("data/metadata.json")
    if os.path.exists("data/season_2025.csv"):
        os.remove("data/season_2025.csv")

Scraper().check()
print("Extracting features and training models...")

if os.path.exists("data/previous_seasons.csv"):
    pd.concat([pd.read_csv("data/previous_seasons.csv"), pd.read_csv("data/season_2025.csv")]).to_csv("data/all_seasons.csv", index=False)

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def convert_time(s):
    if isinstance(s, float):
        return s
    elif not isinstance(s, str) or len(s) < 3:
        return None
    else :
        if len(s) == len("1:00:000"):
            return float(int(s[-3:]))/1000 + int(s[-6:-4]) + 60 * int(s[0])
        
def convert_year(row):
    return row["Position"] * ((row["Year"] - 2000) ** 3)

def convert_team(team):
    team = team.lower()
    if "williams" in team:
        return "Williams"
    elif "haas" in team:
        return "Haas"
    elif "mercedes" in team:
        return "Mercedes"
    elif "red bull" in team:
        return "Red Bull"
    elif "ferrari" in team:
        return "Ferrari"
    elif "sauber" in team:
        return "Sauber"
    elif "aston" in team:
        return "Aston Martin"
    elif "alpine" in team:
        return "Alpine"
    elif any([x in team for x in ["toro", "tauri", "racing bull"]]):
        return "VCARB"
    else:
        return "McLaren"
        
categorical_features = ["TrackId", "Code", "Team"]
numerical_features = ["Q1", "Q2", "Q3", "Grid"]

categorical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder())
])

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler())
])

preprocessor_pre = ColumnTransformer(
    transformers=[
        ("cat", categorical_pipeline, categorical_features)
    ]
)

preprocessor_post = ColumnTransformer(
    transformers=[
        ("cat", categorical_pipeline, categorical_features),
        ("num", numeric_pipeline, numerical_features),
    ]
)

path = "data/all_seasons.csv"
df = pd.read_csv(path)

df.TrackId = df.TrackId.astype(int)
df.Year = df.Year.astype(int)
df.Grid = df.Grid.replace({'\\N':21, 'DQ':21, "NC":21}).astype(float).astype(int)
df.Position = df.Position.replace({'\\N':21, 'DQ':21, "NC":21}).astype(float).astype(int)
df.Position = df.apply(convert_year, axis=1)

df.Q1 = df.Q1.apply(convert_time)
df.Q2 = df.Q2.apply(convert_time)
df.Q3 = df.Q3.apply(convert_time)
df.FastestLap = df.FastestLap.apply(convert_time)

df.Team = df.Team.apply(convert_team)

X = df.drop(["FastestLap", "Position", "Year"], axis=1)
X_no_time = X.drop(["Q1", "Q2", "Q3"], axis=1)
l = df.FastestLap
p = df.Position

preprocessor_pre.fit_transform(X_no_time)
preprocessor_post.fit_transform(X)

joblib.dump(preprocessor_pre, "models/preprocessor_pre.pkl")
joblib.dump(preprocessor_post, "models/preprocessor_post.pkl")

from sklearn.neural_network import MLPRegressor
pre_quali = MLPRegressor(hidden_layer_sizes=(10, 10, 10), max_iter=5000)
post_quali = MLPRegressor(hidden_layer_sizes=(10, 10, 10), max_iter=5000)

pre_quali.fit(preprocessor_pre.transform(X_no_time), p)
post_quali.fit(preprocessor_post.transform(X), p)

joblib.dump(pre_quali, "models/pre_quali.pkl")
joblib.dump(post_quali, "models/post_quali.pkl")
print("Done!")
