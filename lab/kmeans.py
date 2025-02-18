import pandas as pd
import logging
from sklearn.cluster import KMeans

logging.basicConfig(filename='app_log.txt',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
data = pd.read_csv('train.csv')


