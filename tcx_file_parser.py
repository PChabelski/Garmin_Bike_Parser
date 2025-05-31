import xml.etree.ElementTree as ET
import pandas as pd
import dateutil.parser as dp
import glob
import os

# schemas for Garmin TCX files (only choosing the relevant one for biking):
GARMIN_XML_SCHEMAS = {
    'x1': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
}


def tcx_to_df_biking(tcx_file):

    # parse the TCX file for relevant data
    tree = ET.parse(tcx_file)
    root = tree.getroot()
    run = root[0][0]

    data_arr = []
    for lap_number, lap in enumerate(run.findall('x1:Lap', GARMIN_XML_SCHEMAS)):
        for tp in lap.find('x1:Track', GARMIN_XML_SCHEMAS).findall('x1:Trackpoint', GARMIN_XML_SCHEMAS):
            bike_data = {}
            # Extracting data from each Trackpoint
            try:
                bike_data['Time'] = dp.parse(tp.find('x1:Time', GARMIN_XML_SCHEMAS).text)
                bike_data['Latitude'] = float(tp.find('x1:Position', GARMIN_XML_SCHEMAS)[0].text)
                bike_data['Longitude'] = float(tp.find('x1:Position', GARMIN_XML_SCHEMAS)[1].text)
                bike_data['Elevation'] = round(float(tp.find('x1:AltitudeMeters', GARMIN_XML_SCHEMAS).text), 4)
                bike_data['Distance'] = round(float(tp.find('x1:DistanceMeters', GARMIN_XML_SCHEMAS).text), 2)
                bike_data['Heart_rate'] = int(tp.find('x1:HeartRateBpm', GARMIN_XML_SCHEMAS)[0].text)
                bike_data['Speed'] = round(float(tp.find('x1:Extensions', GARMIN_XML_SCHEMAS)[0][0].text), 3)
                bike_data['Lap'] = lap_number + 1
                data_arr.append(bike_data)
            except Exception as e:
                pass

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data_arr)
    # add custom columns for further analysis
    activity_start = df.Time.iloc[0]
    df['Ride ID'] = activity_start
    df['Total_Ride_Distance_km'] = df['Distance'].max()/1000 # in kilometers
    df['Total_Ride_Time_minutes'] = (df['Time'].max() - df['Time'].min()).total_seconds() / 60  # in minutes
    print(f'Processed an activity from {activity_start} with {len(df)} datapoints')
    return df

####### Main execution block to process all TCX files in the specified directory
tcx_dir = os.path.join(os.getcwd(), 'tcx_raw_files')
df_all = pd.DataFrame()

for tcx_file in glob.glob(os.path.join(tcx_dir, '*.tcx')):
    df_all = pd.concat([df_all, tcx_to_df_biking(tcx_file)])

# output the combined dataframe for downstream visualization
df_all.to_csv(f'output/Garmin_Biking_all.csv', index=False)
