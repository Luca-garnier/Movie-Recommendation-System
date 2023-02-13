from api.api import deployAPI
from data.data_collection import DataCollection
from data.train_data_prep import TrainingDataPrep
from data.db import get_connection
from model.model import Model
from monitoring.online_evaluation import OnlineEvaluation


class Pipeline:
    def __init__(self, collect=False, training=False, deploy=True, port=8082):

        self.port = port
        
        if collect == True and (training == True or deploy == True):
            raise "Cannot collect and train or deploy at the same time"

        get_connection()
        self.deploy = deploy
        self.steps = []

        # Data Collection Mode
        if collect:
            print("Collecting data....")
            self.data_collection = DataCollection()
            self.steps = [self.data_collection]

        # Training Mode
        if training:
            print("Training....")
            self.train_data_prep = TrainingDataPrep()
            self.train_model = Model()
            self.steps = [self.train_data_prep, self.train_model]

    def run(self):
        for step in self.steps:
            step.run()
        if self.deploy:
            print("Deploying")
            deployAPI(self.port)


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()
