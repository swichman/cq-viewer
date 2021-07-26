#!/usr/bin/env python3

import maidenhead as mh
import pandas as pd
import sqlite3

class cqDB:
    def __init__(self, db_name='WSJTX.db', log_name='ALL.TXT'):
        try:
            fh = open(str(log_name), 'r');
            fh.close()
        except:
            print(f"No such log file '{filename}'... closing\n")
            exit()

        self.db_name = db_name
        self.log_name = log_name
        self.log_pointer = 0
        self.log_fh = open(self.log_name, 'r')
        self.create_db()

    def create_db(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("CREATE TABLE cq_rx (Timestamp STRING, Frequency FLOAT, Mode STRING, Callsign STRING, Maidenhead STRING, Latitude FLOAT, Longitude FLOAT, SNR FLOAT)")
            cursor.execute("CREATE TABLE cq_tx (Timestamp STRING, Frequency FLOAT, Mode STRING, Callsign STRING, Maidenhead STRING, Latitude FLOAT, Longitude FLOAT, SNR FLOAT)")
        except sqlite3.OperationalError:
            print('Database already exists. Appending new data.')
            pass
        connection.commit()
        connection.close()

    def insert_data(self, data, x):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO {x} VALUES ("{data[0]}",{data[1]},"{data[2]}","{data[3]}","{data[4]}",{data[5]},{data[6]},{data[7]})')
        connection.commit()
        connection.close()

    def insert_rx(self, data):
        self.insert_data(data, 'cq_rx')

    def insert_tx(self, data):
        self.insert_data(data, 'cq_tx')

    def parse_rx(self, fields):
        maidenhead = fields[len(fields)-1]
        callsign = fields[len(fields)-2]
        # ensure that maidenhead is in proper format
        if len(maidenhead) == 4 or len(maidenhead) == 6:
            # convert to lat/lon and store to dataframe
            loc = mh.to_location(maidenhead)
            data = [fields[0], fields[1], fields[3], callsign, maidenhead, loc[0], loc[1], fields[4]]
            self.insert_rx(data)

    def parse_log(self):
        for line in self.log_fh:
            # remove superfluous spaces, and split string into components
            fields = ' '.join(line.split()).split(' ')
            if 'CQ' in fields[7]:
                self.parse_rx(fields)

def wsjtx2df(filename):
    try:
        fh = open(str(filename), 'r')
        fh.close()
    except:
        print(f"No such file {filename}... closing\n")
        exit()

    data = pd.DataFrame()

    # open the WSJT-X log file
    with open(str(filename), 'r') as fh:
        lat = 0
        lon = 0
        i = 0
        for line in fh:
            # remove superfluous spaces, and split string into components
            fields = ' '.join(line.split()).split(' ')
            # look for CQ calls
            if fields[7] != 'CQ':
                continue
            maidenhead = fields[len(fields)-1]
            callsign = fields[len(fields)-2]
            # ensure that maidenhead is in proper format
            if len(maidenhead) == 4 or len(maidenhead) == 6:
                # convert to lat/lon and store to dataframe
                loc = mh.to_location(maidenhead)
                data = data.append( pd.DataFrame({"Timestamp":fields[0],
                                                  "Frequency":fields[1],
                                                  "Mode":fields[3],
                                                  "Callsign":callsign,
                                                  "Maidenhead":maidenhead,
                                                  "Latitude":loc[0],
                                                  "Longitude":loc[1],
                                                  "SNR":fields[4]},
                                                  index=[i]))
                i += 1

    return data

def df2heatmap(df, output='', hm_path=''):
    df = df.sort_values('Maidenhead')
    df = df.reset_index(drop=True)

    heatmap_df = pd.DataFrame()

    old_value = ''
    avg = 0

    for index, row in df.iterrows():
        if row["Maidenhead"] not in old_value and old_value != '' or index == len(df)-1:
            #print(f'MH: {old_value}    <==>    avg: {avg}')
            heatmap_df = heatmap_df.append({"weight":round((avg + 25),0),
                                            "lat":row["Latitude"],
                                            "lon":row["Longitude"]},
                                            ignore_index=True
                                          )
            avg = int(row["SNR"])
            pass
        old_value = row["Maidenhead"]
        avg = ( avg + int(row["SNR"]) ) / 2

    if output != '':
        heatmap_df.to_csv(output + '_heatmap.csv', index=False, sep=';')
        df.to_csv(output + '_CQ-data.csv', index=False)

    js_leaf_out = '''//heatmap data for spots.
var addressPoints = [
'''
    for index, row in heatmap_df.iterrows():
        js_leaf_out += f'[{row["lat"]},{row["lon"]},{row["weight"]/20}],\n'
    js_leaf_out = js_leaf_out[:-2] + '\n];'
    with open(hm_path + '/heatmap.js', 'w') as fh:
        fh.write(js_leaf_out)
    return heatmap_df
