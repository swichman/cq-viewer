#!/usr/bin/env python3

import maidenhead as mh
import pandas as pd
import sqlite3
import datetime

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
        self.db_index = 0
        self.create_db()

    def create_db(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        print('Building Database...')
        try:
            cursor.execute("CREATE TABLE cq_rx (id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp STRING, Frequency FLOAT, Mode STRING, Callsign STRING, Maidenhead STRING, Latitude FLOAT, Longitude FLOAT, SNR FLOAT)")
            cursor.execute("CREATE TABLE cq_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp STRING, Frequency FLOAT, Mode STRING, Callsign STRING, Maidenhead STRING, Latitude FLOAT, Longitude FLOAT, SNR FLOAT)")
        except sqlite3.OperationalError:
            print('Database already exists. Appending new data.')
            # Get the last timestamp entered into the cq_rx database
            max_id = cursor.execute('SELECT max(ID) FROM cq_rx').fetchone()[0]
            last_ts = cursor.execute(f'SELECT Timestamp FROM cq_rx WHERE ID = {max_id}').fetchone()[0]
            print('last timestamp recorded: ' + last_ts)
            print('Finding last position in file...')
            # Find that timestamp in the log file
            ind = 0
            file_pos = -1
            for line in self.log_fh:
                ind += len(line)
                if last_ts in line:
                    file_pos = ind
            if file_pos > 0:
                print(f'Last position found at cursor position {file_pos}. Resuming...')
                self.parse_log()
                self.create_heatmap(0)
            # if timestamp isn't found, close and open file to reset seek cursor.
            if file_pos < 0:
                print('No matching timestamp found for last entry. Data must be from different log file.')
                self.log_fh.close()
                self.log_fh = open(self.log_name, 'r')
        connection.commit()
        connection.close()

    def insert_data(self, data, x):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO {x}(Timestamp, Frequency, Mode, Callsign, Maidenhead, Latitude, Longitude, SNR) VALUES ("{data[0]}",{data[1]},"{data[2]}","{data[3]}","{data[4]}",{data[5]},{data[6]},{data[7]})')
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

        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        max_id = cursor.execute('SELECT max(ID) FROM cq_rx').fetchone()[0]
        if self.db_index == 0:
            print(f'{datetime.datetime.now()} ==> {max_id - self.db_index} entries in database. Following file for new data...')
        else:
            if (max_id - self.db_index) > 0:
                print(f'{datetime.datetime.now()} ==> {max_id - self.db_index} new entries...')
                self.create_heatmap(max_id - self.db_index)
        self.db_index = max_id

    def create_heatmap(self, rows):
        connection = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * from cq_rx", connection)
        if rows > 0:
            print(df.tail(rows))

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

        js_leaf_out = '''//heatmap data for spots.
var addressPoints = [
'''
        for index, row in heatmap_df.iterrows():
            js_leaf_out += f'[{row["lat"]},{row["lon"]},{row["weight"]/20}],\n'
        js_leaf_out = js_leaf_out[:-2] + '\n];'
        with open('cq-heatmap/heatmap.js', 'w') as fh:
            fh.write(js_leaf_out)
