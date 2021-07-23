#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    HDBScan Clustering Algorithm on Division Profiles
    author: Labeeb Khan
    email: labeebk1@gmail.com
"""

import os
import pandas as pd
import numpy as np
import hdbscan
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

if __name__ == "__main__":

    input_folder = '../data/clean_data/'
    input_file_name = 'profiles.pickle'
    output_file_name = 'profiles_with_clusters.csv'
    plot_folder = '../output/Cluster Plots/'

    profile_df = pd.read_pickle(os.path.join(input_folder, input_file_name))

    cluster_data = profile_df.drop('Division', axis=1)

    test_cols = ['Average Expenditure','Stdev of Expenditure','Average Monthly Expenditure CV', \
                    'Average Quarterly Expenditure CV'] + [col for col in cluster_data.columns if 'Merchant' in col]

    cluster_data = cluster_data[test_cols]
    
    # Train the HDBScan clustering algorithm
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, gen_min_span_tree=True)
    clusterer.fit(cluster_data)
    # Save the output to a file
    print(clusterer.labels_)

    import pdb; pdb.set_trace();

    profile_df['Clusters'] = clusterer.labels_
    profile_df.to_csv(os.path.join(input_folder, output_file_name))

    # Generate Cluster Plots
    clusterer.single_linkage_tree_.plot(cmap='viridis', colorbar=True)
    plt.savefig(os.path.join(plot_folder,'single_linkage_tree_3.png'))
    plt.clf()

    clusterer.condensed_tree_.plot()
    plt.savefig(os.path.join(plot_folder,'condensed_tree_3.png'))
    plt.clf()

    clusterer.condensed_tree_.plot(select_clusters=True, selection_palette=sns.color_palette())
    plt.savefig(os.path.join(plot_folder,'condensed_tree_highlight_clusters_3.png'))
    plt.clf()