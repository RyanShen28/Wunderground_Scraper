import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import os

airport_locations = {
    "KMKE": "Milwaukee, Wisconsin",
    "KMSP": "Minneapolis–St. Paul, Minnesota",
    "KFAR": "Fargo, North Dakota",
    "KFSD": "Sioux Falls, South Dakota",
    "KCYS": "Cheyenne, Wyoming",
    "KBOI": "Boise, Idaho",
    "KOMA": "Omaha, Nebraska",
    "KPDX": "Portland, Oregon",
    "KSEA": "Seattle, Washington",
    "KGTF": "Great Falls, Montana",
    "KFNL": "Fort Collins (Loveland), Colorado",
    "KSLC": "Salt Lake City, Utah",
    "KMDW": "Chicago Midway, Illinois",
    "KDSM": "Des Moines, Iowa",
    "KDTW": "Detroit (Metro), Michigan",
    "KIND": "Indianapolis, Indiana",
    "KCLE": "Cleveland, Ohio",
    "KPHL": "Philadelphia, Pennsylvania",
    "KHVN": "New Haven, Connecticut",
    "KBOS": "Boston, Massachusetts",
    "KMHT": "Manchester, New Hampshire",
    "KAUG": "Augusta, Maine",
    "KPVD": "Providence, Rhode Island",
    "KJFK": "New York City (JFK), New York"
}

for filename in airport_locations:
    for y in range(25):
        for m in range(12):
            df = pd.read_csv(filename + '.csv')
            month = m+1
            year = 2000+y

            save_dir = "C:/Users/ryans/Desktop/Projects/Weather_Underground_Web_Scraper/plots/"+airport_locations[filename]
            os.makedirs(save_dir, exist_ok=True, mode=0o666)
            save_path = os.path.join(save_dir, ""+airport_locations[filename]+", Month "+str(month)+", Year "+str(year)+".png")
            print(save_path)


            df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format= '%Y-%m-%d %I:%M %p')

            df = df.sort_values(by='datetime')

            df['Hour'] = df['datetime'].dt.hour
            df['Day'] = df['datetime'].dt.day
            df['Month'] = df['datetime'].dt.month
            df['Year'] = df['datetime'].dt.year


            df = df[(df['Year']== year) & (df['Month']==month)]

            #AUG = augusta, maine, sorts to 2004 January Only




            grouped = df.groupby(['Year', 'Month', 'Day', 'Hour'])['Temperature_C'].transform('mean')
            df['Temperature_C'] = grouped

            df=df.drop_duplicates(subset=['Year', 'Month', 'Day', 'Hour'])

            #fill in missing
            all_days = df['Day'].unique()
            all_hours = df['Hour'].unique()


            full_index = pd.MultiIndex.from_product([all_days, all_hours], names=['Day', 'Hour'])
            df = df.set_index(['Day', 'Hour']).reindex(full_index).reset_index()


            df['Temperature_C'] = df['Temperature_C'].interpolate(method='linear')

            heatmap_data = df.pivot_table(
                columns=['Day'],  # MultiIndex: rows = year + month
                index='Hour',           # Columns = hours (0–23)
                values='Temperature_C',     # Values = temperature
                aggfunc='mean'            # Aggregate if duplicates exist
            )

            plt.figure(figsize=(calendar.monthrange(year, month)[1],24))

            plot = sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, fmt=".1f",
                        cbar_kws={'label': 'Temperature C'}, vmin=-30, vmax=50)



            plot.set_xticklabels(plot.get_xticklabels(), fontsize=25)
            plot.set_yticklabels(plot.get_yticklabels(), fontsize=20)

            plot.set_xlabel("Day", fontsize=33)
            plot.set_ylabel("Hour", fontsize=33)

            plot.collections[0].colorbar.set_label('Temperature (C)', size=25)
            plot.collections[0].colorbar.ax.tick_params(labelsize=18)




            title = 'Hourly Celsius Temperature Data for Year ' + str(year) + ', Month '+ str(month) +' at '+filename

            plot.set_title(title, fontsize=40)

            plt.savefig(save_path, dpi = 300, bbox_inches = 'tight')

            plt.clf()
            del df
            del heatmap_data
            del plot
            plt.close()

