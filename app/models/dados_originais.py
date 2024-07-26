import pandas as pd

class originalData:
    def __init__(self, data, metadata, origem, destino):
        self.data = data
        self.metadata = metadata
        self.origem = origem
        self.destino = destino

        #ordenando cronoologicamente
        self.orderedData = self.data.copy()
        self.orderedData[metadata] = pd.to_datetime(self.data[metadata], dayfirst=True)
        self.orderedData.sort_values(by=metadata, inplace=True)
        self.orderedData.reset_index(inplace=True, drop=True)

    def get_data(self):
        return self.data
    
    def getOriginalOrderedData(self):
        return self.orderedData