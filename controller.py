import joblib, pandas as pd, requests, json
from bs4 import BeautifulSoup
from datetime import date

with open("data/links.json", "r", encoding="utf-8") as f:
    LINKS = json.load(f)

points_map = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}

class Controller:
    def __init__(self):
        self.nn_pre_quali = joblib.load("models/nn_pre_quali.pkl")
        self.nn_post_quali = joblib.load("models/nn_post_quali.pkl")
        self.rf_pre_quali = joblib.load("models/rf_pre_quali.pkl")
        self.rf_post_quali = joblib.load("models/rf_post_quali.pkl")
        self.drivers = pd.read_csv('data/drivers.csv')
        self.preprocessor_post = joblib.load("models/preprocessor_post.pkl")
        self.preprocessor_pre = joblib.load("models/preprocessor_pre.pkl")
        self.team_map = {
            'Alpine F1 Team': "Alpine",
            'Haas F1 Team': "Haas",
            'Toro Rosso': "Racing Bulls",
            'Red Bull Racing': "Red Bull",
            'RB F1 Team': "Red Bull",
            'Racing Point': "Aston Martin",
            'Red Bull Racing Honda RBPT': "Red Bull",
            'Alpine Renault': "Alpine",
            'Aston Martin Aramco Mercedes':'Aston Martin',
            'McLaren Mercedes':"McLaren",
            'Williams Mercedes': "Williams",
            'AlphaTauri Honda RBPT': "Racing Bulls",
            'Haas Ferrari':"Ferrari",
            'RB Honda RBPT':"Red Bull"
        }

    @staticmethod
    def convert_time(s):
        if isinstance(s, float):
            return s
        elif not isinstance(s, str) or len(s) < 3:
            return None
        else :
            if len(s) == len("1:00:000"):
                return float(int(s[-3:]))/1000 + int(s[-6:-4]) + 60 * int(s[0])

    def preprocess_post(self, df):
        df.Team = df.Team.replace(self.team_map)
        df.TrackId = df.TrackId.astype(int)
        df = df.dropna()
        print(df)
        df.loc[df["Grid"].isin(["\\N", "DQ", "NC"]), "Grid"] = 21
        df.loc[:, "Grid"] = df.Grid.astype(float).astype("Int64")
        df.loc[:, "Q1"] = df["Q1"].apply(self.convert_time)
        df.loc[:, "Q2"] = df["Q2"].apply(self.convert_time)
        df.loc[:, "Q3"] = df["Q3"].apply(self.convert_time)

        return self.preprocessor_post.transform(df)

    def preprocess_pre(self, df):
        df.Team = df.Team.replace(self.team_map)
        df.TrackId = df.TrackId.astype(int)
        print(df)
        return self.preprocessor_pre.transform(df)
    
    def extract_qualifying(self, link):
        data = pd.DataFrame(columns=["Code", "Q1", "Q2", "Q3", "Grid"])
        soup = BeautifulSoup(requests.get(link).text, "lxml")
        table = soup.find("tbody")
        rows = table.find_all("tr")

        for row in rows:
            grid, _, name, _, q1, q2, q3, _ = [val.text for val in row.find_all("td")]
            name, code = name[:-3], name[-3:]
            data.loc[len(data)] = [code, q1, q2, q3, grid]
        return data

    def predict(self, args):
        if args['mode'] == "pre_qualifying":
            df = pd.concat([self.drivers, pd.Series([args['track']] * len(self.drivers), name="TrackId")], axis=1)
            df_processed = self.preprocess_pre(df)
            pred_nn = self.nn_pre_quali.predict(df_processed)
            pred_rf = self.rf_pre_quali.predict(df_processed)
            ranking = pd.concat([df.Code, pd.DataFrame(pred_nn + pred_rf, columns=["Pred"])], axis=1).sort_values(by="Pred")
            return list(ranking.Code)
        else:
            df = pd.merge(self.drivers, self.extract_qualifying(args['link']), how='left', on=["Code"])
            df = pd.concat([df, pd.Series([args['track']] * len(self.drivers), name="TrackId")], axis=1)
            df_processed = self.preprocess_post(df)
            pred_nn = self.nn_post_quali.predict(df_processed)
            pred_rf = self.rf_post_quali.predict(df_processed)
            ranking = pd.concat([df.Code, pd.DataFrame(pred_nn + pred_rf, columns=["Pred"])], axis=1).sort_values(by="Pred")

            return list(ranking.Code)
        
    def get_standings(self):
        soup = BeautifulSoup(requests.get("https://www.formula1.com/en/results/2025/drivers").text, 'lxml')
        df = pd.DataFrame([], columns=["Code", "Points"])
        table = soup.find("tbody")
        rows = table.find_all("tr")[:20] 
        
        for row in rows:
            data = row.find_all("td")
            code, points = data[1].text[-3:], data[4].text
            df.loc[len(df)] = [code, points]

        df.loc[:, "Points"] = df.Points.astype(int)
        return df
        
    def predict_season(self):
        current = self.get_standings()
        for link_set in LINKS.values():
            if link_set['day'] > int(date.today().strftime("%j")):
                ranking = self.predict({"mode":"pre_qualifying", 'track':link_set['id']})
                for i in range(10):
                    current.loc[current.Code == ranking[i], "Points"] += points_map[i+1]
        return current.sort_values(by="Points", ascending=False).reset_index(drop=True)

