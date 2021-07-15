#!/usr/bin/env python3

import maidenhead as mh
import pandas as pd

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

def df2heatmap(df):
    df = df.sort_values('Maidenhead')
    df = df.reset_index(drop=True)

    heatmap_df = pd.DataFrame()

    old_value = ''
    avg = 0

    for index, row in df.iterrows():
        if row["Maidenhead"] not in old_value and old_value != '' or index == len(df)-1:
            #print(f'MH: {old_value}    <==>    avg: {avg}')
            heatmap_df = heatmap_df.append({"Latitude":row["Latitude"],
                                            "Longitude":row["Longitude"],
                                            "SNR": round((avg + 25),0)},
                                            ignore_index=True
                                          )
            avg = int(row["SNR"])
            pass
        old_value = row["Maidenhead"]
        avg = ( avg + int(row["SNR"]) ) / 2

    return heatmap_df
