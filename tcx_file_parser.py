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
    print(f'Processed a biking activity from {activity_start} with {len(df)} datapoints')
    return df

#########################################################################################################
def tcx_to_df_running(tcx_file):

    # parse the TCX file for relevant data
    tree = ET.parse(tcx_file)
    root = tree.getroot()
    run = root[0][0]

    data_arr = []
    for lap_number, lap in enumerate(run.findall('x1:Lap', GARMIN_XML_SCHEMAS)):
        for tp in lap.find('x1:Track', GARMIN_XML_SCHEMAS).findall('x1:Trackpoint', GARMIN_XML_SCHEMAS):
            run_data = {}
            # Extracting data from each Trackpoint
            try:
                run_data['Time'] = dp.parse(tp.find('x1:Time', GARMIN_XML_SCHEMAS).text)
                run_data['Latitude'] = float(tp.find('x1:Position', GARMIN_XML_SCHEMAS)[0].text)
                run_data['Longitude'] = float(tp.find('x1:Position', GARMIN_XML_SCHEMAS)[1].text)
                run_data['Elevation'] = round(float(tp.find('x1:AltitudeMeters', GARMIN_XML_SCHEMAS).text), 4)
                run_data['Distance'] = round(float(tp.find('x1:DistanceMeters', GARMIN_XML_SCHEMAS).text), 2)
                run_data['Heart_rate'] = int(tp.find('x1:HeartRateBpm', GARMIN_XML_SCHEMAS)[0].text)
                run_data['Speed'] = round(float(tp.find('x1:Extensions', GARMIN_XML_SCHEMAS)[0][0].text), 3)
                run_data['Lap'] = lap_number + 1
                data_arr.append(run_data)
            except Exception as e:
                pass

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data_arr)
    # add custom columns for further analysis
    activity_start = df.Time.iloc[0]
    df['Run ID'] = activity_start
    df['Total_Run_Distance_km'] = df['Distance'].max()/1000 # in kilometers
    df['Total_Run_Time_minutes'] = (df['Time'].max() - df['Time'].min()).total_seconds() / 60  # in minutes
    print(f'Processed a running activity from {activity_start} with {len(df)} datapoints')
    return df



#########################################################################################
####### Main execution block to process all BIKING TCX files in the specified directory
tcx_bike_dir = os.path.join(os.getcwd(), 'tcx_bike_files')
df_all_biking = pd.DataFrame()

for tcx_file in glob.glob(os.path.join(tcx_bike_dir, '*.tcx')):
    df_all_biking = pd.concat([df_all_biking, tcx_to_df_biking(tcx_file)])

# output the combined dataframe for downstream visualization
df_all_biking.to_csv(f'output/Garmin_Biking_all.csv', index=False)
print('Biking data processing complete and saved to output/Garmin_Biking_all.csv\n\n')
#########################################################################################
####### Main execution block to process all RUNNING TCX files in the specified directory
tcx_run_dir = os.path.join(os.getcwd(), 'tcx_run_files')
df_all_running = pd.DataFrame()

for tcx_file in glob.glob(os.path.join(tcx_run_dir, '*.tcx')):
    df_all_running = pd.concat([df_all_running, tcx_to_df_running(tcx_file)])

# output the combined dataframe for downstream visualization
df_all_running.to_csv(f'output/Garmin_Running_all.csv', index=False)
print('Running data processing complete and saved to output/Garmin_Running_all.csv\n\n')
