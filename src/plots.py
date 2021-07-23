
import os
import plotly.graph_objs as go
from plotly.offline import plot
from pandas.api.types import is_numeric_dtype

def single_one_way_graph(x_var, y_vars, df, plot_type, plot_title, file_path, file_name, save=True)->go.Figure:
    """
    This function produces an html one-way plot for a y_var vs a given x_var.\

    Args:
        df (dataframe): table containing all x_var, y_vars, weight
        x_var (str): name of the variable to plot on the x-axis
        y_vars (str or list): name or lists of names of the variables to plot on the y-axis
        file_path (str): path at which to save the plot
        save (bool): whether or not to save the plot at the specified file_path

    Returns:
        fig (go.Figure): plotly figure object of one way graph
    """

    def __plot_graph(df_agg, y_vars, x_var, plot_type, plot_title, file_path, file_name, is_numeric=True, save=True):
        figure_data = list()
        for y_var in y_vars:
            if plot_type == 'Bar':
                figure_data.append(go.Bar(x=df_agg[x_var], y=df_agg[y_var], name=f'{y_var}', yaxis='y'))
            if plot_type == 'Line':
                figure_data.append(go.Scatter(x=df_agg[x_var], y=df_agg[y_var], name=f'{y_var}', yaxis='y'))

        layout = go.Layout(
            title=plot_title,
            yaxis=dict(
                title=f'{y_vars}'
            ),
            xaxis=dict(
                title=x_var
            )
        )

        fig = go.Figure(data=figure_data, layout=layout)

        if not is_numeric:
            fig.update_layout(xaxis_type='category')

        if save:
            plot(fig, filename=os.path.join(file_path, file_name + '.html'), auto_open=False)

        return fig

    if type(y_vars) != list:
        y_vars = [y_vars]  # just in case string is passed to y_vars rather than a list

    fig = __plot_graph(df, y_vars, x_var, plot_type, plot_title, file_path, file_name,
                        is_numeric=is_numeric_dtype(df[x_var]), save=save)

    return fig

def one_way_graph(x_vars, y_vars, df, file_path, file_name, plot_type, plot_title):
    """
    This function produces an html one-way plot for a y_var vs a given x in each x_vars list.

    This functions calls single_one_way_graph function if x_vars is a a single element. If x_vars contains multiple
    elements it will call the single_one_way_graph and run over all variables in x_vars list

    Args:
        df (dataframe): table containing all x_var, y_vars, weight
        x_vars (str or list): name or lists of names for x_axis of all plots
        y_vars (str or list): name or lists of names of the variables to plot on the y-axis
        file_path (str): path at which to save the plot

    """
    if type(y_vars) != list:
        y_vars = [y_vars]  # just in case string is passed to y_vars rather than a list

    if type(x_vars) == list:
        for x_var in x_vars:
            single_one_way_graph(x_var, y_vars, df, plot_type, plot_title, file_path, file_name, save=True)

    else:
        single_one_way_graph(x_vars, y_vars, df, plot_type, plot_title, file_path, file_name, save=True)
