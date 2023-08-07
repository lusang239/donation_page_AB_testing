import pandas as pd

from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder
from sklearn.preprocessing import StandardScaler 
from sklearn.linear_model import LinearRegression, LogisticRegression


class UserPredictor:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        
    def fit(self, train_users, train_logs, train_y):
        
        # data preprocessing 
        self.training_data, self.training_trans, self.training_features = self.data_preprocessing(train_users, train_logs)
        
        # Select features to train
        #self.xcols = ['past_purchase_amt']
        self.xcols = self.training_features
        
        # build the data pipeline 
        #pipe = Pipeline([
        #    ("poly", PolynomialFeatures(degree=2)),
        #    ("std", StandardScaler()),
        #    ("lr", self.model)
        #])
        pipe = Pipeline([
            ("trans", self.training_trans),
            ("lr", self.model)
        ])

       
        self.model_after = pipe.fit(self.training_data[self.xcols], train_y['y'])
        
        # return the model
        return self.model_after
    
    def predict(self, test_users, test_logs):
        
        # data preprocessing 
        self.testing_data, self.testing_trans, self.testing_features = self.data_preprocessing(test_users, test_logs)
        
        # select feature to test and store in dataframe 
        #y_preds = self.model_after.predict(test_users[self.xcols])
        y_preds = self.model_after.predict(self.testing_data[self.testing_features])
        
        # return numpy array
        return y_preds
    
    def data_preprocessing(self, users, logs):
        
        # get the frequency of total time, count of url
        logs_total_seconds = logs.groupby('user_id', as_index=False).agg({"seconds": "sum",
                                                                       "url": "count"})
        
        # combine two table
        data = pd.merge(users, logs_total_seconds, how='left', left_on="user_id", right_on="user_id")
        
        data = data.rename(columns = {"seconds": "total_seconds", "url": "url_count"})
        
        # fill NaN value
        data["total_seconds"] = data.total_seconds.fillna(0)
        data["url_count"] = data.url_count.fillna(0)
        
        # transform 
        trans = make_column_transformer(
            (OneHotEncoder(), ["badge"]),
            (PolynomialFeatures(degree=2), ["past_purchase_amt", "total_seconds", "url_count"]),
            (StandardScaler(), ["past_purchase_amt", "total_seconds", "url_count"])
        )
        
        features = ["age", "past_purchase_amt", "badge", "total_seconds", "url_count"]
        
        return data, trans, features
