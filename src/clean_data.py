#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Data Processing Script for PCard Expenditures
    author: Labeeb Khan
    email: labeebk1@gmail.com
"""

import os
import xlrd
import pdb
import time
import pandas as pd

class Dataset:
    """
    A class to represent a raw Dataset file (xls or xlsx).

    Attributes:
        folder_path (string): path to the folder containing the datasets
        file_name (string): name of the file including the extension
        df (dataframe): dataframe representation of the dataset
        file_path (string): path to the dataset file
        column_names (list): standardized names of columns for the PCardExpenses datasets

    Methods:
        load_data: reads the excel file into a pandas DataFrame
        clean_data: imputes the DataFrame based on missing values and standardizes column names
        closest_match: finds the closest match of a string within a list of strings
        validate_data: checks if any column values are null or there exists any columns outside the standardized column names
    """
    def __init__(self, folder_path, file_name):
        # Only consider files with extension type 'xls' or 'xlsx'
        if 'xls' not in file_name[-4:].lower():
            raise Exception(
                "Error: Dataset loaded must be of extension type 'xls' or 'xlsx'.")

        self.folder_path = folder_path
        self.file_name = file_name
        self.file_path = os.path.join(self.folder_path, self.file_name)
        self.__load_data()

    def __load_data(self):
        try:
            self.df = pd.read_excel(self.file_path)
        except xlrd.biffh.XLRDError:
            self.df = pd.read_excel(self.file_path, engine='openpyxl')
        except Exception:
            print("An error occurred loading the dataset.")

    def clean_data(self):
        # Drop unnamed columns
        unnamed_columns = [
            col for col in self.df.columns if 'unnamed' in col.lower()]
        self.df.drop(
            labels=unnamed_columns,
            axis=1,
            inplace=True
        )

        # Some G/L Account Descriptions in the raw data are named differently
        self.df.rename(
            columns={
                'Long Text': 'G/L Account Description',
                'Exp Type Desc': 'G/L Account Description'
            },
            inplace=True,
            errors='ignore'
        )

        # Column names across workbooks are incorrectly named. Keep a consistent naming convention
        self.column_names = [
            'Division', 'Batch-Transaction ID', 'Transaction Date', 'Card Posting Dt', 'Merchant Name', 'Transaction Amt.',
            'Transaction Currency', 'Original Amount', 'Original Currency', 'G/L Account', 'G/L Account Description',
            'Cost Centre / WBS Element', 'Cost Centre / WBS Element Description', 'Merchant Type', 'Merchant Type Description',
            'Purpose'
        ]

        # Validate each column - find the closest match to the column_names list and rename input DataFrame
        for column in self.df.columns:
            if column not in self.column_names:
                matched_column = self.__closest_match(column, self.column_names)
                self.df.rename(
                    columns={column: matched_column},
                    inplace=True,
                    errors='ignore'
                )

        # Typo in Report: PCardExpenses_201203_Final.xls
        if 'Transaction Currency' not in self.df.columns:
            print(f"Modified: {self.df.columns.values[6]} to: Transaction Currency")
            self.df.columns.values[6] = 'Transaction Currency'

        # Some data have extra blank columns. Subset and re-order the DataFrame columns for the column_names
        self.df = self.df[self.column_names]

        # Drop rows that contain na values in the Division nd Batch-Transaction ID column. The raw data has subtotals by division that need dropping
        self.df = self.df[~((self.df['Division'].isna()) &
                            self.df['Batch-Transaction ID'].isna())]

        # Purpose column can be blank
        self.df.loc[self.df['Purpose'].isna(), 'Purpose'] = ''

        # Missing Transaction dates can be assigned to their corresponding Card posting date
        self.df['Transaction Date'].fillna(self.df['Card Posting Dt'], inplace=True)

        # TODO: Missing Divisions, Cost Centre, Merchant Type. Email the city of Toronto to understand why there are missing values. Assign it to 'MISSING' for now.
        for column_name in ['Division', 'Cost Centre / WBS Element', 'Cost Centre / WBS Element Description', 'Merchant Type']:
            self.df.loc[self.df[column_name].isna(), column_name] = 'MISSING'

        # Assign a file name so data can be referenced back to the original raw datasets
        self.df['Source'] = self.file_name

        # For consistent naming of the divisions, we can convert the names to title-case and strip any whitespaces in the beginning/end
        self.df['Division'] = self.df['Division'].apply(lambda x: x.title().strip())

    # Find the column name within a pre-defined list that has the closest match to the desired column
    def __closest_match(self, search_value, names):
        match_count = 0
        best_match = names[0]
        for name in names:
            num_letters_matched = len(set(name) & set(search_value))

            if num_letters_matched > match_count:
                match_count = num_letters_matched
                best_match = name

        return best_match

    def validate_data(self):
        # Check if there exists no NaN values in the DataFrame post processing
        nan_counts = self.df.isna().sum()
        total_nans = sum(nan_counts)
        nan_summary = nan_counts[nan_counts > 0]

        if total_nans > 0:
            # Debugger to investigate why there are NaNs
            pdb.set_trace()

        assert total_nans == 0, f'NaN exist in DataFrame for report: {self.file_name} for columns: \n {str(nan_summary)}'

        # Check for any missing columns
        assert len(self.df.columns) == len(
            self.column_names) + 1, f'Missing columns in DataFrame for report: {self.file_name}'


if __name__ == '__main__':
    raw_data_path = '../data/raw_data/'
    output_data_path = '../data/clean_data/'

    # Get list of file names from the raw_data folder
    expense_report_names = [name for name in os.listdir(
        raw_data_path) if 'xls' in name[-4:].lower()]

    output_df = pd.DataFrame()

    start = time.time()

    for report_name in expense_report_names:
        print(f"Processing Dataset: {report_name}")
        dataset = Dataset(
            folder_path=raw_data_path,
            file_name=report_name
        )
        dataset.clean_data()
        dataset.validate_data()

        # Concatenate along indeces
        output_df = pd.concat([output_df, dataset.df])

        # Delete the object in memory
        del dataset

    # Impute the divisions based on an existing mapping file (created manually)
    divisions_map = pd.read_csv('./divisions_map.csv')
    divisions_map_dict = {}
    for _, row in divisions_map.iterrows():
        if row['Division (From)'] != row['Division (To)']:
            divisions_map_dict[
                row['Division (From)']
            ] = row['Division (To)']

    output_df['Division'].replace(divisions_map_dict, inplace=True)

    output_df['Year'] = output_df['Transaction Date'].apply(lambda x: x.year)
    output_df['Month'] = output_df['Transaction Date'].apply(lambda x: x.month)
    output_df['Year-Month'] = output_df['Transaction Date'].apply(lambda x: x.strftime('%Y-%m'))
    output_df['Quarter'] = pd.PeriodIndex(output_df['Transaction Date'], freq='Q')

    # Remove 2010 data
    output_df = output_df[output_df['Year'] != 2010]

    # Convert Columns to Categories
    for col_name in ['Merchant Type', 'G/L Account', 'Cost Centre / WBS Element', 'Transaction Currency']:
        output_df[col_name] = output_df[col_name].astype('category')
        output_df[col_name + '_code'] = output_df[col_name].cat.codes

    end = time.time()
    duration = round(end - start, 2)
    print(f"Total Processing Time: {duration} seconds")

    # Save the output to a pickle file. Faster read/write times. Feather file format is also a good option.
    output_df.to_pickle(os.path.join(output_data_path, 'PCardExpenses_Clean_201101-201907.pickle'))
