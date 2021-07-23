#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Exploratory Data Analysis
    author: Labeeb Khan
    email: labeebk1@gmail.com
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
from plots import one_way_graph

class Profile:
    def __init__(self, df, division_name, merchants, plot_folder):
        self.df = df
        self.division_name = division_name
        self.merchants = merchants

        # Create output folder for this profile
        self.plot_folder = plot_folder
        if not os.path.exists(self.plot_folder):
            os.mkdir(self.plot_folder)

        self.profile = {}
        self.profile['Division'] = self.division_name

        # Assign a count of 0 to each merchant. Values will get mapped on in __get_merchant_dist
        for merchant in self.merchants:
            self.profile[f'Merchant_{merchant}_count'] = 0

        # Average and Standard Deviation of Expenditures
        self.profile['Average Expenditure'] = np.average(self.df['Transaction Amt.'])
        self.profile['Stdev of Expenditure'] = np.std(self.df['Transaction Amt.'])

        # Time series plots on Monthly and Quarterly Expenditures and their CV
        self.__get_monthly_expenditures()
        self.__get_quarterly_expenditures()
        self.__get_cost_centre_dist()
        self.__get_gl_accounts_dist()
        self.__get_currencies_dist()
        self.__get_merchant_dist()

    def __get_monthly_expenditures(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('Year-Month').agg(
            {'Transaction Amt.': ['sum', 'mean']}
        )
        # Flatten the multi-index columns. TODO: There is probably a better way to do this.
        summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]

        summary_df = summary_df.rename(columns={
            'Transaction Amt._sum': 'Total Expenditure',
            'Transaction Amt._mean': 'Average Expenditure'
        }).reset_index()

        for y_var in ['Total Expenditure', 'Average Expenditure']:
            one_way_graph(
                x_vars=['Year-Month'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Line',
                plot_title = f'{y_var} by Month for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by Month'
            )

        self.profile['Average Monthly Expenditure CV'] = stats.variation(summary_df['Average Expenditure'])

    def __get_quarterly_expenditures(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('Quarter').agg(
            {'Transaction Amt.': ['sum', 'mean']}
        )
        # Flatten the multi-index columns. TODO: There is probably a better way to do this.
        summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]

        summary_df = summary_df.rename(columns={
            'Transaction Amt._sum': 'Total Expenditure',
            'Transaction Amt._mean': 'Average Expenditure'
        }).reset_index()

        # Convert from datetime[64] to string for plotting
        summary_df['Quarter'] = summary_df['Quarter'].astype(str)

        for y_var in ['Total Expenditure', 'Average Expenditure']:
            one_way_graph(
                x_vars=['Quarter'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Line',
                plot_title = f'{y_var} by Quarter for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by Quarter'
            )
            
        self.profile['Average Quarterly Expenditure CV'] = stats.variation(summary_df['Average Expenditure'])

    def __get_cost_centre_dist(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('Cost Centre / WBS Element').agg({
            'Batch-Transaction ID': 'count',
            'Transaction Amt.': ['sum', 'mean'],
        })
        # Flatten the multi-index columns. TODO: There is probably a better way to do this.
        summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]

        summary_df = summary_df.rename(columns={
            'Batch-Transaction ID_count': 'Count',
            'Transaction Amt._sum': 'Total Expenditure',
            'Transaction Amt._mean': 'Average Expenditure'
        }).reset_index().sort_values(by='Count', ascending=False)
            
        summary_df = summary_df[summary_df['Count'] > 0]

        for y_var in ['Count', 'Total Expenditure', 'Average Expenditure']:
            one_way_graph(
                x_vars=['Cost Centre / WBS Element'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Bar',
                plot_title = f'{y_var} by Cost Centre for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by Cost Centre'
            )

        self.profile['Total Cost Centres'] = summary_df.shape[0]
        
        freq_list = []
        for idx, count in enumerate(summary_df['Count'].to_list()):
            freq_list = freq_list + [idx] * count

        self.profile['Count by Cost Centre Skew'] = stats.skew(freq_list)
        self.profile['Count by Cost Centre Kurtosis'] = stats.kurtosis(freq_list)

    def __get_merchant_dist(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('Merchant Type').agg({
            'Batch-Transaction ID': 'count',
            'Transaction Amt.': ['sum', 'mean'],
        })
        # Flatten the multi-index columns. TODO: There is probably a better way to do this.
        summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]

        summary_df = summary_df.rename(columns={
            'Batch-Transaction ID_count': 'Count',
            'Transaction Amt._sum': 'Total Expenditure',
            'Transaction Amt._mean': 'Average Expenditure'
        }).reset_index().sort_values(by='Count', ascending=False)

        summary_df = summary_df[summary_df['Count'] > 0]

        for y_var in ['Count', 'Total Expenditure', 'Average Expenditure']:
            one_way_graph(
                x_vars=['Merchant Type'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Bar',
                plot_title = f'{y_var} by Merchant Type for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by Merchant Type'
            )

        self.profile['Total Merchants'] = summary_df.shape[0]
        
        freq_list = []
        for idx, count in enumerate(summary_df['Count'].to_list()):
            freq_list = freq_list + [idx] * count

        self.profile['Count by Merchant Skew'] = stats.skew(freq_list)
        self.profile['Count by Merchant Kurtosis'] = stats.kurtosis(freq_list)

        # Get Frequency of Merchants by Division
        summary_df['Freq'] = summary_df['Count']/summary_df['Count'].sum()

        for _, row in summary_df.iterrows():
            self.profile['Merchant_' + str(row['Merchant Type']) + '_count'] = row['Freq']

    def __get_gl_accounts_dist(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('G/L Account').agg({
            'Batch-Transaction ID': 'count',
            'Transaction Amt.': ['sum', 'mean'],
        })
        # Flatten the multi-index columns. TODO: There is probably a better way to do this.
        summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]

        summary_df = summary_df.rename(columns={
            'Batch-Transaction ID_count': 'Count',
            'Transaction Amt._sum': 'Total Expenditure',
            'Transaction Amt._mean': 'Average Expenditure'
        }).reset_index().sort_values(by='Count', ascending=False)

        summary_df = summary_df[summary_df['Count'] > 0]

        for y_var in ['Count', 'Total Expenditure', 'Average Expenditure']:
            one_way_graph(
                x_vars=['G/L Account'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Bar',
                plot_title = f'{y_var} by G/L Account for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by GL Account'
            )

        self.profile['Total G/L Accounts'] = summary_df.shape[0]
        
        freq_list = []
        for idx, count in enumerate(summary_df['Count'].to_list()):
            freq_list = freq_list + [idx] * count

        self.profile['Count by G/L Account Skew'] = stats.skew(freq_list)
        self.profile['Count by G/L Account Kurtosis'] = stats.kurtosis(freq_list)      

    def __get_currencies_dist(self):
        # Plot of average and total expenditures by month
        summary_df = self.df.groupby('Original Currency').agg({
            'Batch-Transaction ID': 'count',
        }).reset_index()
        
        summary_df.rename(columns={'Batch-Transaction ID': 'count'}, inplace=True)
        summary_df.sort_values(by='count', ascending=False)

        summary_df = summary_df[summary_df['count'] > 0]

        for y_var in ['count']:
            one_way_graph(
                x_vars=['Original Currency'],
                y_vars=[y_var],
                df=summary_df,
                plot_type='Bar',
                plot_title = f'{y_var} by Original Currency for {self.division_name}',
                file_path=self.plot_folder,
                file_name=f'{y_var} by Original Currency'
            )

        self.profile['Total Currencies'] = summary_df.shape[0]

if __name__ == '__main__':
    folder_path = '../data/clean_data/'
    file_name = 'PCardExpenses_Clean_201101-201907.pickle'

    df = pd.read_pickle(os.path.join(folder_path, file_name))

    divisions = df['Division'].value_counts().index.to_list()
    merchants = df['Merchant Type'].value_counts().index.to_list()

    division_profiles = []

    for division in divisions:
        # Create Folder for each Division, if it doesn't already exist
        output_folder = os.path.join('../output/Division Plots/', division)

        # Subset dataset by division
        division_df = df[df['Division'] == division]

        division_profile = Profile(
            df=division_df,
            division_name=division,
            merchants=merchants,
            plot_folder = output_folder
        )

        print(f'Generating Profile for: {division}')
        division_profiles.append(division_profile.profile)
        print(division_profile.profile)

    profiles_df = pd.DataFrame(division_profiles)
    profiles_df.to_pickle('../data/clean_data/profiles.pickle')
    profiles_df.to_csv('../data/clean_data/profiles.csv')

    plot_metrics = ['Average Expenditure', 'Stdev of Expenditure', 'Average Monthly Expenditure CV', 'Average Quarterly Expenditure CV', 
                    'Total Cost Centres', 'Count by Cost Centre Skew', 'Count by Cost Centre Kurtosis', 'Total Merchants', 'Count by Merchant Skew',
                    'Count by Merchant Kurtosis', 'Total G/L Accounts', 'Count by G/L Account Skew', 'Count by G/L Account Kurtosis', 'Total Currencies']
    for y_var in plot_metrics:
        file_name = y_var.replace('/','') + ' by Divisions'
        one_way_graph(
            x_vars=['Division'],
            y_vars=[y_var],
            df=profiles_df,
            plot_type='Bar',
            plot_title = f'{y_var} by Divisions',
            file_path='../output/Divisions Summary/',
            file_name=file_name
        )
