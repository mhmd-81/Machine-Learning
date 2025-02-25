import pandas as pd
import logging
from sklearn.cluster import KMeans

logging.basicConfig(filename='app_log.txt',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class read_data(object):
    def __init__(self):
        self.data = None

    def load_data(self, file_path):
        try:
            # Attempt to read the CSV file
            self.data = pd.read_csv(file_path)
            logging.info(f"Data loaded successfully from {file_path}")
            return self.data
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"The file at {file_path} could not be found.")
        except pd.errors.ParserError:
            logging.error(f"Error parsing file: {file_path}")
            raise ValueError(f"There was an error parsing the file at {file_path}.")
        except Exception as e:
            logging.error(f"An error occurred while reading the file: {e}")
            raise Exception(f"An error occurred while reading the file: {e}")


class data_processing(object):
    def __init__(self, data):
        self.data = data
        self.numeric_columns = []
        self.categorical_columns = []

    def check_column_types(self):
        if self.data is not None:
            # Select numeric columns
            self.numeric_columns = self.data.select_dtypes(include=['number']).columns.tolist()

            # Select categorical columns (exclude numeric ones)
            self.categorical_columns = self.data.select_dtypes(exclude=['number']).columns.tolist()

            logging.info(f"Numeric columns: {self.numeric_columns}")
            logging.info(f"Categorical columns: {self.categorical_columns}")
        else:
            logging.error("Data is not loaded.")
            raise ValueError("Data is not loaded.")

    # def perform_kmeans(self, n_clusters=3):
    #     if self.data is not None:
    #         try:
    #             if len(self.numeric_columns) == 0:
    #                 raise ValueError("There are no numeric columns for clustering.")
    #
    #             # Perform KMeans clustering on the numeric columns
    #             kmeans = KMeans(n_clusters=n_clusters)
    #             kmeans.fit(self.data[self.numeric_columns])
    #             logging.info(f"KMeans clustering performed with {n_clusters} clusters")
    #             return kmeans
    #         except Exception as e:
    #             logging.error(f"An error occurred while performing KMeans: {e}")
    #             raise Exception(f"An error occurred while performing KMeans: {e}")
    #     else:
    #         raise ValueError("Data is not loaded.")


# Example usage
if __name__ == "__main__":
    file_path = input("Please enter the path to the CSV file: ")

    # Load the data using the read_data class
    data_reader = read_data()
    try:
        data = data_reader.load_data(file_path)
        print("Data loaded successfully!")

        # Pass the loaded data to another class (data_processing)
        data_processor = data_processing(data)

        # Check column types (numeric or categorical)
        data_processor.check_column_types()

        # Perform some data processing (e.g., KMeans clustering on numeric columns)
        kmeans_model = data_processor.perform_kmeans(n_clusters=3)
        print("KMeans clustering performed.")

    except Exception as e:
        print(f"Error: {e}")
