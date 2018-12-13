"""
IS 590PR - Programming for Analytics & Data Processing
Final Project- Simulating the probability of the estimated fines that a single occupancy vehicles will have to pay.

Authors:
Aditya Kadrekar
Ankita Pant
Devanshi Bhatt

Important abbreviations used in the code:
sov ~ single occupancy vehicles
hov ~ high occupancy vehicles
gpv ~ general purpose vehicles

Note:
The ranges for all randomized values have been considered based on the real data
obtained from various sources that are cited in the README document of github repository of the project.
"""

from random import choice, randint, choices
#from collections import Counter, defaultdict
#import typing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Lanes:

    def __init__(self):
        self.num_sov = 0
        self.num_hov = 0
        self.weather=''
        self.weather_int=0
        self.accident=''
        self.accident_intensity=int

    def rand_gen_pert(self, low, likely, high, confidence=4, samples=10):
        """Produce random numbers according to the 'Modified PERT' distribution.

        :param low: The lowest value expected as possible.
        :param likely: The 'most likely' value, statistically, the mode.
        :param high: The highest value expected as possible.
        :param confidence: This is typically called 'lambda' in literature
                            about the Modified PERT distribution. The value
                            4 here matches the standard PERT curve. Higher
                            values indicate higher confidence in the mode.
                            Currently allows values 1-18

        Formulas from "Modified Pert Simulation" by Paulo Buchsbaum.
        """

        mean = (low + confidence * likely + high) / (confidence + 2.0)
        a = (mean - low) / (high - low) * (confidence + 2)
        b = ((confidence + 1) * high - low - confidence * likely) / (high - low)

        beta = np.random.beta(a, b, samples)
        beta = beta * (high - low) + low
        return beta

    def fn_weather_int(self, no_of_samples):
        """
        This function defines the weather and its intensity on a scale of 1 to 10
        with 10 being the worst weather.
        3 main seasons considered: Summer, Winter, Rains.
        Seasons are randomly chosen for every sample with weights assigned to each season.
        'Modified PERT' distribution is used for the random selection of weather intensity.

        :param no_of_samples: Number of samples the user wants to consider for the simulation
        :return: list with all weather intensities
        """

        p = no_of_samples
        df['weather'] = choices(['Summer', 'Winter', 'Rains'], [0.5, 0.3, 0.2], k=p)
        weather_int_list=[]

        for season in df['weather']:
            if season == 'Summer':
                #weather in Summer does not affect the performance of an HOV lane.
                #so the intensty is set to zero in this case.
                weather_int=0

            elif season == 'Winter':
                weather_int= np.median(self.rand_gen_pert(1, 4, 10, samples=10))

            else:
                weather_int= np.median(self.rand_gen_pert(1, 5, 10, samples=10))

            weather_int_list.append(round(weather_int, 2))
            #df['weather_int'] = pd.DataFrame(weather_int_list)

        return weather_int_list

    def fn_accident_int(self, no_of_samples):
        """
        This function checks for occurrence of an accident on the HOV lane.
        If yes, then the number of accidents per day has been randomized.
        'Modified PERT' distribution is used for the random selection of no. of accidents with
        minimum 1 accident, maximum 10 accidents and most likely 5 accidents.

        :param no_of_samples: Number of samples the user wants to consider for the simulation
        :return: list with number of accidents
        """

        p = no_of_samples
        df['accident'] = choices(['Yes', 'No'], [0.6, 0.4], k=p)
        no_of_accidents_list = []

        for value in df['accident']:
            if value == 'No':
                no_of_accidents = 0
            else:
                no_of_accidents = np.median(self.rand_gen_pert(1, 5, 10, samples=10))

            no_of_accidents_list.append(round(no_of_accidents, 0))
            # df['no_of_accidents'] = pd.DataFrame(no_of_accidents_list)
            # df['accident_fine'] = df['no_of_accidents'] * 100

        return no_of_accidents_list

    def fn_compute_avgspeed(self):
        """
        This function randomizes the speed of vehicles on both, HOV and general purpose lanes.
        The speed of vehicles depends on weather, number of accidents and the number of vehicles in each lane.
        'Modified PERT' distribution is used for the random generation of speed.
        """

        hov_speed_list = []
        gpv_speed_list = []

        for index, row in df.iterrows():
            if (row['weather'] == 'Winter' or row['weather'] == 'Rains') and row['weather_int'] > 3 \
                    and row['no_of_accidents'] > 3 and (row['hov'] > 1400 or row['gpv'] < 1500):
                speed = round(np.median(self.rand_gen_pert(35, 45, 75, samples=10)), 2)
                gpv_speed = round(np.median(self.rand_gen_pert(25, 35, 50, samples=10)), 2)
                hov_speed_list.append(speed)
                gpv_speed_list.append(gpv_speed)
            else:
                speed = round(np.median(self.rand_gen_pert(70, 80, 85, samples=10)), 2)
                gpv_speed = round(np.median(self.rand_gen_pert(35, 45, 60, samples=10)), 2)
                hov_speed_list.append(speed)
                gpv_speed_list.append(gpv_speed)

        # df['hov_speed (mph)'] = pd.DataFrame(hov_speed_list)
        # df['gpv_speed (mph)'] = pd.DataFrame(gpv_speed_list)

        return hov_speed_list, gpv_speed_list

    # @staticmethod
    # def fn_compute_avgtime():
    #     """
    #     This function computes the average time required by the vehicles to travel
    #     on the HOV and general purpose lanes.
    #     The length of both the lanes is considered to be 20 miles.
    #
    #     :return: None
    #     """
    #     df['hov_time'] = round(20/df['hov_speed (mph)'], 2)
    #     df['gpv_time'] = round(20/df['gpv_speed (mph)'], 2)
    #
    #     return

    @staticmethod
    def fn_compute_pollution():
        """
        This function calculates the total emissions (in grams) of pollutants from vehicles
        in case of both HOV and general purpose lanes.
        Pollutant emitted: Carbon Monoxide.

        :return:
        """

        hov_pol_emiss_list = []
        gvp_pol_emiss_list = []

        # emissions in a general purpose lane
        for index, row in df.iterrows():
            if (row['gpv_speed (mph)']) < 40:
                # 211 grams of CO is emitted when the speed of vehicle is less than 40 mph
                gpv_pol_emiss = 211
                gvp_pol_emiss_list.append(gpv_pol_emiss)
            else:
                #181 grams of CO is emitted when the speed of vehicle is greater than 40 mph
                gpv_pol_emiss = 181
                gvp_pol_emiss_list.append(gpv_pol_emiss)
        df['gpv_emis'] = pd.DataFrame(gvp_pol_emiss_list)

        #emissions in the HOV lane
        for index, row in df.iterrows():
            if (row['hov_speed (mph)']) < 60:
                #151 grams of CO emitted when speed of vehicle on an HOV lane is less than 60mph
                hov_pol_emiss = 151
                hov_pol_emiss_list.append(hov_pol_emiss)
            else:
                #CO emissions are reduced by 78 grams if vehicle speed on HOV lane is greater than 60mph
                hov_pol_emiss = 211 - 78
                hov_pol_emiss_list.append(hov_pol_emiss)
        df['hov_emis'] = pd.DataFrame(hov_pol_emiss_list)

        return hov_pol_emiss_list, gvp_pol_emiss_list

    def fn_vehicles(self, no_of_samples):
        """
        This function generates random values for the number of HOV and SOV vehicles on the HOV lane.
        It also randomizes teh number of vehicles in general purpose lane.
        The number of fuel-efficient or hybrid SOV vehicles is also taken into consideration
        which is 20% of the total SOV vehicles on the HOV lane.
        It is assumed that 70% of fuel-efficient SOV vehicles are registered to drive on the HOV lane.
        'Modified PERT' distribution is used for the random number generation.

        :param no_of_samples: Number of samples the user wants to consider for the simulation
        :return: None
        """

        p = no_of_samples

        # Randomizing a given hour of the day to be peak with 50% chances
        df['peak_hour'] = choices(['Yes', 'No'], [0.5, 0.5], k=p)
        hov_list, sov_list, fuel_eff_list, fuel_eff_reg_list, fuel_eff_non_reg_list, gpv_list = ([] for i in range(6))

        # Generating random values for number of SOV , HOV based on online statistical data
        for i in df['peak_hour']:

            #there are more number of vehicles in peak hours than in non-peak hours
            if i == 'Yes':
                hov_vehicles = round(np.median(self.rand_gen_pert(1080, 1440, 1740, samples=10)), 0)
                sov_vehicles = round(np.median(self.rand_gen_pert(150, 200, 300, samples=10)), 0)
                # general purpose vehicles decreases during peak hour as they move to hov lane
                gpv_vehicles = round(np.median(self.rand_gen_pert(1000, 1250, 1500, samples=10)), 0)
            else:
                hov_vehicles = round(np.median(self.rand_gen_pert(660, 1080, 1680, samples=10)), 0)
                sov_vehicles = round(np.median(self.rand_gen_pert(50, 100, 200, samples=10)), 0)
                # general purpose vehicles increases during non peak hour as there is no hov lane
                gpv_vehicles = round(np.median(self.rand_gen_pert(1500, 2000, 2200, samples=10)), 0)

            #number of  fuel-efficient/hybrid vehicles and registered fuel-efficient/hybrid vehicles
            fuel_eff_vehicles = 0.2 * sov_vehicles
            reg_fuel_eff = 0.7 * fuel_eff_vehicles

            # Appending the calculated values to the Dataframe
            hov_list.append(hov_vehicles)
            sov_list.append(sov_vehicles)
            gpv_list.append(gpv_vehicles)
            fuel_eff_list.append(round(fuel_eff_vehicles, 0))
            fuel_eff_reg_list.append(round(reg_fuel_eff, 0))

        # df['hov'] = pd.DataFrame(hov_list)
        # df['sov'] = pd.DataFrame(sov_list)
        # df['gpv'] = pd.DataFrame(gpv_list)
        # df['fuel_efficient_sov'] = pd.DataFrame(fuel_eff_list)
        # df['reg_fuel_eff'] = pd.DataFrame(fuel_eff_reg_list)

        return hov_list, sov_list, fuel_eff_list, fuel_eff_reg_list, fuel_eff_non_reg_list, gpv_list

    # def fn_fine(self):
    #     """
    #     This function calculates the estimated fine that is collected in a day from all the SOV vehicles
    #     that are either non-hybrid or are hybrid but non-registered for using the HOV lane.
    #     Fine amount is fixed- $450.
    #     Fine is calculated only for the 4 peak hours of a day.
    #
    #     :return: None
    #     """
    #
    #     df['estimate_fine'] = (df['sov'] - df['reg_fuel_eff']) * 450 * 4
    #     return

    # def fn_camera_functional(self, no_of_samples):
    #     """
    #     Calculating actual fine earned by the state depending on the camera functionality.
    #     It is assumed that the cameras are functional 80% of the time.
    #
    #     :param no_of_samples: User input
    #     :return: None
    #     """
    #
    #     p=no_of_samples
    #     df['camera_functional'] = choices(['Yes', 'No'], [0.8, 0.2], k=p)
    #
    #     ## Plotting distribution of Functionality of Camera
    #     # plt.hist(df['camera_functional'], density=False)
    #     # plt.title('Distribution of Camera Functionality')
    #
    #     df['actual_fine'] = np.where(df['camera_functional'] == 'Yes', (0.8 * (df['sov'] - df['reg_fuel_eff']) * 450 * 4),
    #                                  0)
    #     return

def fn_camera_functional(no_of_samples):
    """
    Calculating actual fine earned by the state depending on the camera functionality.
    It is assumed that the cameras are functional 80% of the time.

    :param no_of_samples: User input
    :return: None
    """

    p=no_of_samples
    df['camera_functional'] = choices(['Yes', 'No'], [0.8, 0.2], k=p)

    # Plotting distribution of Functionality of Camera
    # plt.hist(df['camera_functional'], density=False)
    # plt.title('Distribution of Camera Functionality')

    df['actual_fine'] = np.where(df['camera_functional'] == 'Yes', (0.8 * (df['sov'] - df['reg_fuel_eff']) * 450 * 4),
                                     0)
    return

def fn_fine():
    """
    This function calculates the estimated fine that is collected in a day from all the SOV vehicles
    that are either non-hybrid or are hybrid but non-registered for using the HOV lane.
    Fine amount is fixed- $450.
    Fine is calculated only for the 4 peak hours of a day.

    :return: None
    """

    df['estimate_fine'] = (df['sov'] - df['reg_fuel_eff']) * 450 * 4
    return

def fn_compute_avgtime():
    """
    This function computes the average time required by the vehicles to travel
    on the HOV and general purpose lanes.
    The length of both the lanes is considered to be 20 miles.

    :return: None
    """
    df['hov_time'] = round(20/df['hov_speed (mph)'], 2)
    df['gpv_time'] = round(20/df['gpv_speed (mph)'], 2)

    return

if __name__ == '__main__':

    samples_list=list(range(50, 1000, 50 ))
    print(samples_list)

    try:
        print('More the number of samples for simulation, better is the accuracy of predicted values\n')
        no_of_samples = int(input('Enter the number of samples in power of 10: '))

        if no_of_samples in samples_list:
            pass
        else:
            no_of_samples = int(input('Please enter a number which is power of 10: '))

    except Exception as e:
        print(e)

    df = pd.DataFrame(columns=['peak_hour', 'hov', 'sov', 'gpv', 'fuel_efficient_sov', 'reg_fuel_eff',
                               'camera_functional', 'weather', 'weather_int', 'accident', 'no_of_accidents', 'accident_fine',
                               'hov_speed (mph)', 'gpv_speed (mph)', 'hov_time', 'gpv_time', 'hov_emis', 'gpv_emis', 'estimate_fine',
                               'actual_fine', 'revenue_lost_per_day'])

    my_lane = Lanes()
    weather_int_list = my_lane.fn_weather_int(no_of_samples)
    df['weather_int'] = pd.DataFrame(weather_int_list)
    no_of_accidents_list = my_lane.fn_accident_int(no_of_samples)
    df['no_of_accidents'] = pd.DataFrame(no_of_accidents_list)
    df['accident_fine'] = df['no_of_accidents'] * 100
    hov_list, sov_list, fuel_eff_list, fuel_eff_reg_list, fuel_eff_non_reg_list, gpv_list = my_lane.fn_vehicles(no_of_samples)
    df['hov'] = pd.DataFrame(hov_list)
    df['sov'] = pd.DataFrame(sov_list)
    df['gpv'] = pd.DataFrame(gpv_list)
    df['fuel_efficient_sov'] = pd.DataFrame(fuel_eff_list)
    df['reg_fuel_eff'] = pd.DataFrame(fuel_eff_reg_list)
    fn_fine()
    fn_camera_functional(no_of_samples)
    hov_speed_list, gpv_speed_list = my_lane.fn_compute_avgspeed()
    df['hov_speed (mph)'] = pd.DataFrame(hov_speed_list)
    df['gpv_speed (mph)'] = pd.DataFrame(gpv_speed_list)
    fn_compute_avgtime()
    hov_pol_emiss_list, gvp_pol_emiss_list = my_lane.fn_compute_pollution()
    df['gpv_emis'] = pd.DataFrame(gvp_pol_emiss_list)
    df['hov_emis'] = pd.DataFrame(hov_pol_emiss_list)

    # Calculating revenue lost by the state because of the functionality issues with Camera
    df['revenue_lost_per_day'] = df['estimate_fine'] - df['actual_fine']
    df.to_csv('HOV.csv')

    # OUTPUT
    # ------------------------------------------------------------------------------------------------------------------
    print('The below output is considering the hov lane timings and how it consequently affects the general purpose lane - ')
    print('The average speed for high occupancy vehicles per day is {:>{width}.{prec}f} mph'.format(np.mean(df['hov_speed (mph)']), width=12, prec=3))
    print('The average speed for general purpose lane vehicles per day is {:>{width}.{prec}f} mph'.format(np.mean(df['gpv_speed (mph)']), width=0, prec=3), '\n')

    print('The average time (in hours) taken by high occupancy vehicles to cover a 20 mile stretch is {:>{width}.{prec}f}'.format(np.mean(df['hov_time']), width=11, prec=3))
    print('The average time (in hours) taken by general purpose lane vehicles to cover a 20 mile stretch is {:>{width}.{prec}f}'.format(np.mean(df['gpv_time']), width=0, prec=3),'\n')

    print('The average carbon monoxide emission by high occupancy vehicles is {:>{width}.{prec}f}'.format(np.mean(df['hov_emis']), width=12, prec=2), 'grams')
    print('The average carbon monoxide emission by general purpose lane vehicles is {:>{width}.{prec}f}'.format(np.mean(df['gpv_emis']), width=0, prec=2), 'grams\n')

    print('The average estimated revenue the state should be collecting per day is ' + str(np.mean(df['estimate_fine'])))
    print('The average actual revenue the state is collecting per day is ' + str(np.mean(df['actual_fine'])))
    print('The average revenue lost per day by the state is ' + str(np.mean(df['revenue_lost_per_day'])))
    # ------------------------------------------------------------------------------------------------------------------

    ## Plotting Estimated Fine , Actual Fine and Revenue lost per day in histograms
    # hist1 = df.hist(column='estimate_fine', bins=10)
    # plt.show()
    # hist2 = df.hist(column='actual_fine', bins=10)
    # plt.show()
    # hist3 = df.hist(column='revenue_lost_per_day', bins=10)
    # plt.show()

