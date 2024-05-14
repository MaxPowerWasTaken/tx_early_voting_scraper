import os
import pandas as pd
import time
from datetime import datetime
from glob import glob
from tqdm import tqdm

def combine_results(downloads_folder):
    # for each csv file in downloads_folder with name like ev_turnout_*.csv...
    files = glob(os.path.join(downloads_folder, 'ev_turnout_*.csv'))
    final_df = pd.DataFrame()
    for f in tqdm(files):
        df = pd.read_csv(f)
        datepart = datetime.strptime(f.split('_')[-1].split('.')[0], '%Y%m%d')

        df['filedate'] = datepart
        final_df = pd.concat([final_df, df])

    return final_df

if __name__ == "__main__":
    df = combine_results('downloaded_files')
    print(f"Number of records: {len(df):,}; Number of unique `ID_VOTER`s: {df.ID_VOTER.nunique():,}")

    # get those duplicate records - filter df on only ID_VOTER values that are not unique
    duplicates = df[df.duplicated(subset='ID_VOTER', keep=False)].sort_values('filedate')

    # output both sets of results
    df.to_csv('combined_results.csv', index=False)
    duplicates.to_csv('duplicate_id_voter_records.csv', index=False)