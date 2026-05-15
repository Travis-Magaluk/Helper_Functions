import pandas as pd



def reduce_to_nps_numbers_not_sent_to_ITS(dataframe_to_reduce):

    _df = pd.read_csv('data/processed_data/ITS_send/CRIS_Data_Import_4_29_25.csv')

    nps_numbers_sent_to_its = _df['NPSProjectNumber'].copy()

    reduced_dataframe = dataframe_to_reduce[~dataframe_to_reduce['NPSProjectNumber'].isin(nps_numbers_sent_to_its)]

    return reduced_dataframe