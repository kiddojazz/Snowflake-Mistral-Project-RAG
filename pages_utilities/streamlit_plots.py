# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 00:50:27 2024

@author: olanr
"""

import streamlit as st
import plotly.express as px
import time
import pandas as pd
import numpy as np
from typing import Union, List
import plotly.figure_factory as ff
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from functools import wraps
import threading
from uuid import uuid4


# def title_decorator():
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args,**kwargs):
#             st.write(f"Args: {args}")
#             st.write(f"{kwargs = }")
#             st.markdown(f"### {kwargs['title']}")
#             result = func(*args, **kwargs)
#             st.markdown("---")
#             return result
#         return wrapper
#     return decorator

def title_decorator():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Map positional arguments to parameter names
            arg_names = func.__code__.co_varnames
            all_args = dict(zip(arg_names, args))
            all_args.update(kwargs)  # Merge with keyword arguments
            
            title = all_args.get("title", "Untitled Chart")  # Extract title
            st.markdown(f"### {title}")
            result = func(*args, **kwargs)
            st.markdown("---")
            return result
        return wrapper
    return decorator

        
@title_decorator()
def plot_line_chart(df, x_col, y_col, title):
    """
    Plots a line chart using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      title: Title of the chart.
    """
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    key = f"line_key_{x_col}_{y_col}_{chart_num}"
    st.write(key)
    
    st.session_state.df_line = df.copy()
    
    if st.session_state.df_line is not None:
        df = st.session_state.df_line.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    
    if pd.api.types.is_datetime64_any_dtype(df[x_col]):
        try:
            min_date, max_date = df[x_col].min(), df[x_col].max()
            
            new_min_date, new_max_date = st.date_input("select date range", [min_date, max_date], key = key)
            
            max_date_mask = df[x_col] <= datetime(new_max_date.year, new_max_date.month, new_max_date.day)
            min_date_mask = df[x_col] >= datetime(new_min_date.year, new_min_date.month, new_min_date.day)
            filtered_df = df.loc[(max_date_mask & min_date_mask), :]
            
            fig = px.line(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(e)
            fig = px.line(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        
    elif pd.api.types.CategoricalDtype(df[x_col]):
        try:
            cat_vals = list(df[x_col].unique())
            
            if len(cat_vals) > 10:
                start_cat, end_cat = st.select_slider(f"Choose value range for {x_col}",
                                                      options= cat_vals,
                                                      value = (cat_vals[0], cat_vals[-1]), key= key)
                start_idx, end_idx = cat_vals.index(start_cat), cat_vals.index(end_cat)
                selection = cat_vals[start_idx, end_idx + 1]
                
            else:
                selection = st.pills(f"Choose value(s) for {x_col}", cat_vals, selection_mode= "multi", key= key)
                selection_mask = df[x_col].isin(selection)
            
            filtered_df = df.loc[selection_mask, :]
            fig = px.line(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(e)
            fig = px.line(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        
    else:
        fig = px.line(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig)
    

      
@title_decorator()
def plot_bar_chart(df, x_col, y_col, title):
    """
    Plots a bar chart using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      title: Title of the chart.
    """
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"bar_key_{x_col}_{y_col}_{chart_num}"
    st.write(key)
    
    st.session_state.df_bar = df.copy()
    
    if st.session_state.df_bar is not None:
        df = st.session_state.df_bar.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
        
    if pd.api.types.is_categorical_dtype(df[x_col]) or df[x_col].dtype == "object":
        try:
            cat_vals = list(df[x_col].unique())
            selection = st.pills(f"Choose value(s) for {x_col}", cat_vals, selection_mode= "multi", key= key)
                
            selection_mask = df[x_col].isin(selection)
            filtered_df = df.loc[selection_mask, :]
            fig = px.bar(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        
        except Exception as e:
            st.warning(e)
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
            
    elif pd.api.types.is_integer_dtype(df[x_col]):
        try:
            cat_vals = list(df[x_col].unique())
            
            selection = st.pills(f"Choose value(s) for {x_col}", cat_vals, selection_mode= "multi", key= key)
            selection_mask = df[x_col].isin(selection)
            
            filtered_df = df.loc[selection_mask, :]
            fig = px.bar(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
            
        except Exception as e:
            st.warning(e)
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
    
    else:
        try:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        except ValueError:
            pass
    

@title_decorator()
def plot_scatter_chart(df, x_col, y_col, color_col = None, title = "",):
    """
    Plots a scatter chart using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      title: Title of the chart.
    """
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"scatter_key_{x_col}_{y_col}_{chart_num}"

    st.write(key)
    
    st.session_state.df_scatter = df.copy()
    
    if st.session_state.df_scatter is not None:
        df = st.session_state.df_scatter
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    num_step = 20.0
    try:
        if "x_step" not in st.session_state:
            st.session_state.x_step = df[x_col].quantile(0.75)/num_step
        
        x_limit = st.number_input(f"Insert Limit for {x_col}", None, step = st.session_state.x_step, format="%0.2f", key= key)
        
        x_limit_mask= df[x_col] <= x_limit
        
        filtered_df = df.loc[x_limit_mask, :]
        
        color_col = color_col if color_col else x_col
        
        fig = px.scatter(filtered_df, x=x_col, y=y_col, title=title, color = color_col, hover_name=color_col)
        st.plotly_chart(fig)
    
    except Exception as e:
        st.warning(e)
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig)
        

@title_decorator()
def plot_histogram(df, col, title):
    """
    Plots a histogram using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      col: Name of the column to use for the histogram.
      title: Title of the chart.
    """
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"hist_key_{col}_{chart_num}"

    st.write(key)
    
    st.session_state.df_hist = df.copy()
    
    if st.session_state.df_hist is not None:
        df = st.session_state.df_hist.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not col in df.columns:
        st.warning(f"{col}  not found in the dataframe.\ndf={df}")
        return
    
    
    num_step = 20
    try:
        if "x_hist_step" not in st.session_state:
            st.session_state.x_hist_step = df[col].quantile(0.75)/num_step
        
        x_limit = st.number_input(f"Insert Limit for {col}", None, step = st.session_state.x_hist_step, format="%0.2f", key= key)
        
        x_limit_mask= df[col] <= x_limit
        
        filtered_df = df.loc[x_limit_mask, :]
        
        fig = px.histogram(filtered_df, x=col, title=title)
        st.plotly_chart(fig)
        
    except Exception as e:
        st.warning(e)
        fig = px.histogram(df, x=col, title=title)
        st.plotly_chart(fig)


@title_decorator()
def plot_hbar_chart(df, values, names, title, num_bars: int = 10):
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"hbar_key_{values}_{names}_{chart_num}"

    st.write(key)
    
    st.session_state.df_hbar = df.copy()
    
    if st.session_state.df_hbar is not None:
        df = st.session_state.df_hbar.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not values in df.columns:
        st.warning(f"{values}  not found in the dataframe.\ndf={df}")
        return
        
    if names not in df.columns:
        st.warning(f"{names}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        if "hbar_min" not in st.session_state:
            st.session_state.hbar_min = df[values].min()
        
        if "hbar_max" not in st.session_state:
            st.session_state.hbar_max = df[values].max()
            
        if "df_hbar" not in st.session_state:
            st.session_state.df_hbar = df
        
        df = st.session_state.df_hbar
        
        hbar_min = st.session_state.hbar_min
        hbar_max = st.session_state.hbar_max
        
        limits = st.slider(f"Insert Limit for {values}", hbar_min, hbar_max, (hbar_min, hbar_max))
        up_limit_mask= df[values] <= limits[-1]
        low_limit_mask = df[values] >= limits[0]
        
        filtered_df = df.loc[(low_limit_mask & up_limit_mask), :]
        
        options = list(filtered_df[names].unique())
        selection = st.pills(f"Select {names}", options, selection_mode= "multi", key= key)
        selection_mask = filtered_df[names].isin(selection)
        
        filtered_df = filtered_df.loc[selection_mask, :]
        
        fig = px.bar(filtered_df, x = values, y = names, title = title, orientation= "h")
        st.plotly_chart(fig)
        
    except Exception as e:
        st.warning(e)
        fig = px.bar(df, x = values, y = names, title = title, orientation= "h")
        st.plotly_chart(fig)
    

@title_decorator()
def plot_pie_chart(df, values, names, title = "", max_categories: int = 10):
    """
    Plots a pie chart using Plotly Express.

      Args:
        df: Pandas DataFrame containing the data.
        values: Name of the column containing the values for the pie slices.
        names: Name of the column containing the labels for the pie slices.
        title: Title of the chart.
    """
    
    st.session_state.df_pie = df.copy()
    
    if st.session_state.df_pie is not None:
        df = st.session_state.df_pie.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not values in df.columns:
        st.warning(f"{values}  not found in the dataframe.\ndf={df}")
        return
        
    if names not in df.columns:
        st.warning(f"{names}  not found in the dataframe.\ndf={df}")
        return
    
    
    if len(df[names].unique()) < max_categories:
        fig = px.pie(df, values=values, names=names, title=title)
        st.plotly_chart(fig)
        
    else:
        if df[values].dtype in ["int64", "int32", "int16", "int8", "float64", "float32", "float16"]:
            plot_hbar_chart(df, values, names, title)
        
      
     
@title_decorator()
def plot_area_chart(df, x_col, y_col, title):
    """
    Plots an area chart using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      title: Title of the chart.
    """
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"area_key_{x_col}_{y_col}_{chart_num}"

    st.write(key)
    
    st.session_state.df_area = df.copy()
    
    if st.session_state.df_area is not None:
        df = st.session_state.df_area.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    if pd.api.types.is_datetime64_any_dtype(df[x_col]):
        try:
            min_date, max_date = df[x_col].min(), df[x_col].max()
            
            new_min_date, new_max_date = st.date_input("select date range", [min_date, max_date], key= key)
            
            max_date_mask = df[x_col] <= datetime(new_max_date.year, new_max_date.month, new_max_date.day)
            min_date_mask = df[x_col] >= datetime(new_min_date.year, new_min_date.month, new_min_date.day)
            filtered_df = df.loc[(max_date_mask & min_date_mask), :]
            
            fig = px.area(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(e)
            fig = px.area(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        
    elif pd.api.types.CategoricalDtype(df[x_col]):
        try:
            cat_vals = list(df[x_col].unique())
            
            if len(cat_vals) > 10:
                start_cat, end_cat = st.select_slider(f"Choose value range for {x_col}",
                                                      options= cat_vals,
                                                      value = (cat_vals[0], cat_vals[-1]), key= key)
                start_idx, end_idx = cat_vals.index(start_cat), cat_vals.index(end_cat)
                selection = cat_vals[start_idx, end_idx + 1]
                
            else:
                selection = st.pills(f"Choose value(s) for {x_col}", cat_vals, selection_mode= "multi")
                selection_mask = df[x_col].isin(selection)
            
            filtered_df = df.loc[selection_mask, :]
            fig = px.area(filtered_df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
        except Exception as e:
            st.warning(e)
            fig = px.area(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
    else:
        fig = px.area(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig)

@title_decorator()
def plot_box_plot(df, x_col, y_col, title):
    """
    Plots a box plot using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis (categorical).
      y_col: Name of the column to use for the y-axis (numerical).
      title: Title of the chart.
    """
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"box_key_{x_col}_{y_col}_{chart_num}"

    st.write(key)
        
    st.session_state.df_box = df.copy()
    
    if st.session_state.df_box is not None:
        df = st.session_state.df_box.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        
        options = list(df[x_col].unique())
        selection = st.pills(f"Select {x_col}", options, selection_mode= "multi", key= key)
        selection_mask = df[x_col].isin(selection)
        
        filtered_df = df.loc[selection_mask, :]
        fig = px.box(filtered_df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig)
    except Exception as e:
        st.warning(e)
        fig = px.box(df, x=x_col, y=y_col, title=title)
        st.plotly_chart(fig)

@title_decorator()
def plot_heatmap(df, x_col, y_col, values, title, num_vals: int = 10):
    """
    Plots a heatmap using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      values: Name of the column containing the values for the heatmap.
      title: Title of the chart.
    """
    # df_numeric = df.select_dtypes(include = ["int64", "int32", "int16", "int8", "float64", "float32", "float16"])
    # fig = px.imshow(df_numeric.corr(), color_continuous_scale = "BuPu", title=title, text_auto='.2f')
    
    st.session_state.df_heat = df.copy()
    
    if st.session_state.df_heat is not None:
        df = st.session_state.df_heat.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        df_top_n = df.nlargest(num_vals, values)
        heatmap_data = df_top_n.pivot_table(
            index= x_col,
            columns = y_col,
            values = values,
            fill_value= 0
            )
        
        fig = px.imshow(heatmap_data, title = title, text_auto= True)
        fig.update_layout(
            width=1800,  # Width of the heatmap
            height=1800,  # Height of the heatmap   
        )
        
        fig.update_traces(
            textfont = dict(size = 18)
            )
        st.plotly_chart(fig)
    except Exception as e:
        st.warning(e)
        return

@title_decorator()
def plot_bubble_chart(df, x_col, y_col, size_col, title):
    """
    Plots a bubble chart using Plotly Express.
    
    Args:
      df: Pandas DataFrame containing the data.
      x_col: Name of the column to use for the x-axis.
      y_col: Name of the column to use for the y-axis.
      size_col: Name of the column to use for the size of the bubbles.
      title: Title of the chart.
    """
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"bubble_key_{x_col}_{y_col}_{chart_num}"

    st.write(key)
    
    st.session_state.df_bubble = df.copy()
    
    if st.session_state.df_bubble is not None:
        df = st.session_state.df_bubble.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
    
    if not x_col in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
        
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        
        num_step = 20.0
        try:
            if "x_bubble_step" not in st.session_state:
                st.session_state.x_bubble_step = df[x_col].quantile(0.75)/num_step
            
            x_limit = st.number_input(f"Insert Limit for {x_col}", None, step = st.session_state.x_bubble_step, format="%0.2f", key= key)
            
            x_limit_mask= df[x_col] <= x_limit
            
            filtered_df = df.loc[x_limit_mask, :]
            
            color_col = size_col if size_col else x_col
            
            fig = px.scatter(filtered_df, x=x_col, y=y_col, title=title, color = color_col, hover_name=color_col)
            st.plotly_chart(fig)
        
        except Exception as e:
            st.warning(e)
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig)
    
    except Exception as e:   
        st.warning(e)
        fig = px.scatter(df, x=x_col, y=y_col, size=size_col, title=title)
        st.plotly_chart(fig)

@title_decorator()
def plot_sunburst_chart(df, path, values, title):
  """
  Plots a sunburst chart using Plotly Express.

  Args:
    df: Pandas DataFrame containing the data.
    path: A list of columns representing the hierarchical path.
    values: Name of the column containing the values for the sunburst chart.
    title: Title of the chart.
  """
  
  st.session_state.df_sun = df.copy()
  
  if st.session_state.df_sun is not None:
      df = st.session_state.df_sun.copy()
  
  if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
      st.warning("DataFrame is empty")
      return
    
  if values not in df.columns:
      st.warning(f"{values}  not found in the dataframe.\ndf={df}.\ndf={df}")
      return
  
  fig = px.sunburst(df, path=path, values=values, title=title)
  st.plotly_chart(fig)
  

@title_decorator()
def plot_choropleth_map(df, hover_column, location_column, color_column, title = ""):
    
    st.session_state.df_map = df.copy()
    
    if st.session_state.df_map is not None:
        df = st.session_state.df_map.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if hover_column not in df.columns:
        st.warning(f"{hover_column}  not found in the dataframe.\ndf={df}\ndf = {df}")
        return
    
    if location_column not in df.columns:
        st.warning(f"{location_column}  not found in the dataframe.\ndf={df}")
        return
    
    
    df = st.session_state.df_map
    
    fig = px.choropleth(
        df,
        locations=location_column,
        color=color_column,
        hover_name=hover_column,
        title=title,
        projection="orthographic"
        )
    st.plotly_chart(fig)
    
             
@title_decorator()
def plot_kde_plot(df: Union[pd.Series, pd.DataFrame], 
                  group_labels: Union[List, None] = None, 
                  curve_type: str = "kde", 
                  show_hist:bool = True,
                  title: str = ""
                  ):
    
    st.session_state.df_kde = df.copy()
    
    if st.session_state.df_kde is not None:
        df = st.session_state.df_kde.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    
    
    if isinstance(df, pd.Series):
        fig = ff.create_distplot([list(df)],
                                 group_labels= group_labels if group_labels else [df.name],#group_labels,
                                 curve_type=curve_type,
                                 show_hist=show_hist,
                                 )
    else:
        lol_df = [list(df[column]) for column in df.columns]
        fig = ff.create_distplot(lol_df,
                                 group_labels= df.columns,
                                 curve_type=curve_type,
                                 show_hist=show_hist
                                 )
        
    st.plotly_chart(fig)

@title_decorator()
def plot_violin_chart(df, x_col, y_col, color_col = None, box = True, points = "all", title = "Violin Plot"):
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key1 = f"violin_key1_{chart_num}"
    key2 = f"violin_key2_{chart_num}"
    
    st.session_state.df_violin = df.copy()
    
    if st.session_state.df_violin is not None:
        df = st.session_state.df_violin.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if x_col not in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
    
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    x_vals = list(df[x_col].unique())
    x_selection = st.pills(f"Choose value(s) for {x_col}", x_vals, selection_mode= "multi", key= key1)
    x_selection_mask = df[x_col].isin(x_selection)
    df = df.loc[x_selection_mask, :]    
    
    if color_col:
        color_col_vals = list(df[color_col].unique())
        color_selection = st.pills(f"Choose value(s) for {color_col}", color_col_vals, selection_mode= "multi", key= key2)
        color_selection_mask= df[color_col].isin(color_selection)
        df = df.loc[color_selection_mask, :]    
    
    fig = px.violin(
    df,
    y=y_col,
    x=x_col,
    color= color_col,
    box=box,
    points=points,
    title=title
    )

    st.plotly_chart(fig)


@title_decorator()
def plot_funnel_chart(df, x_col, y_col, title = "Sales Funnel"):
    
    st.session_state.df_funnel = df.copy()
    
    if st.session_state.df_funnel is not None:
        df = st.session_state.df_funnel.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if x_col not in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
    
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    
    fig = px.funnel(df, x=x_col, y=y_col, title=title)
    st.plotly_chart(fig)    


@title_decorator()
def plot_treemap_chart(df, path: List, values_col, color_col = None, title = "Treemap Example"):
    
    st.session_state.df_treemap = df.copy()
    
    if st.session_state.df_treemap is not None:
        df = st.session_state.df_treemap.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if values_col not in df.columns:
        st.warning(f"{values_col}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        max_val = df[values_col].max()
        min_val = df[values_col].min()
        
        selected_val = st.slider(f"Choose a value for {values_col}", min_val, max_val, (min_val, max_val))
        
        selection_mask = ((df[values_col] >= selected_val[0]) & (df[values_col] <= selected_val[-1]))
        filtered_df = df.loc[selection_mask, :]
        
        
        fig = px.treemap(
            filtered_df,
            path=path,
            values=values_col,
            color= color_col,
            title=title
            )
    
        st.plotly_chart(fig)
        
    except Exception as e:
        st.warning(e)
        fig = px.treemap(
            df,
            path=path,
            values=values_col,
            color= color_col,
            title=title
            )
    
        st.plotly_chart(fig)

@title_decorator()
def plot_density_heatmap(df, x_col, y_col, title = "Density Heatmap Example"):
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    st.session_state.df_density = df.copy()
    
    if st.session_state.df_density is not None:
        df = st.session_state.df_density.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if x_col not in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return
    
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    fig = px.density_heatmap(
        df,
        x=x_col,
        y=y_col,
        marginal_x="histogram",
        marginal_y="histogram",
        title= title
        )
    st.plotly_chart(fig)


@title_decorator()
def plot_parallel_coordinates(df, dimensions: List[str], color_col, title = "Parallel Coordinates Example"):
    
    st.session_state.df_parallel = df.copy()
    
    if st.session_state.df_parallel is not None:
        df = st.session_state.df_parallel.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if color_col not in df.columns:
        st.warning(f"{color_col}  not found in the dataframe.\ndf={df}")
        return
    
    fig = px.parallel_coordinates(
        df,
        dimensions=dimensions,
        color=color_col,
        title=title
        )
    st.plotly_chart(fig)


@title_decorator()
def plot_timeline_chart(df, x_start, x_end, y_col, color_col, title = "Timeline Example"):
    
    st.session_state.df_timeline = df.copy()
    
    if st.session_state.df_timeline is not None:
        df = st.session_state.df_timeline.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return
    
    fig = px.timeline(
        df,
        x_start=x_start,
        x_end=x_end,
        y=y_col,
        color=color_col,
        title=title
    )
    st.plotly_chart(fig)

@title_decorator()
def plot_3D_scatter_plot(df, x_col, y_col, z_col, color_col = None, title = "3D Scatter Plot Example"):
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"3d_scatter_key_{x_col}_{y_col}_{chart_num}"
    
    st.session_state.df_3d_scatter = df.copy()
    
    if st.session_state.df_3d_scatter is not None:
        df = st.session_state.df_3d_scatter.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if x_col not in df.columns:
        st.warning(f"{x_col}  not found in the dataframe.\ndf={df}")
        return

    if y_col not in df.columns:
        st.warning(f"{y_col}  not found in the dataframe.\ndf={df}")
        return

    if z_col not in df.columns:
        st.warning(f"{z_col}  not found in the dataframe.\ndf={df}")
        return
    
    try:
        
        if color_col:
            color_options = list(df[color_col].unique())
            color_selection = st.pills(f"Select the {color_col}", color_options, selection_mode= "multi", key= key)
            selection_mask = df[color_col].isin(color_selection)
            df = df.loc[selection_mask, :]
        
        fig = px.scatter_3d(
            df,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col,
            title=title
            )
        st.plotly_chart(fig)
    
    except Exception as e:
        st.warning(e)
        fig = px.scatter_3d(
            df,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col,
            title=title
            )
        st.plotly_chart(fig)

@title_decorator()
def plot_radar_chart(df, unique_label_col, aggregated_values_column, chart_name='Performance', title="Radar Chart Example"):
    
    st.session_state.chart_idx += 1
    chart_num = st.session_state.chart_idx
    
    key = f"radar_key_{unique_label_col}_{aggregated_values_column}_{chart_num}"
    
    st.session_state.df_radar = df.copy()
    
    if st.session_state.df_radar is not None:
        df = st.session_state.df_radar.copy()
    
    if not isinstance(df, Union[pd.DataFrame, pd.Series]) or len(df) == 0:
        st.warning("DataFrame is empty")
        return
      
    if unique_label_col not in df.columns:
        st.warning(f"{unique_label_col}  not found in the dataframe.\ndf={df}")
        return
    
    if aggregated_values_column not in df.columns:
        st.warning(f"{aggregated_values_column}  not found in the dataframe.\ndf={df}")
        return
    
    # Group and aggregate data
    new_df = df.groupby(unique_label_col)[aggregated_values_column].sum().reset_index()
    
    
    radar_options = list(df[unique_label_col].unique())
    radar_selection = st.pills(f"Select the {unique_label_col}", radar_options, selection_mode= "multi", key= key)
    selection_mask = new_df[unique_label_col].isin(radar_selection)
    new_df = df.loc[selection_mask, :]
    
    st.write(new_df)
    
    # Create the radar chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=new_df[aggregated_values_column],  # Radial values
        theta=new_df[unique_label_col],    # Categories/angles
        fill='toself',               # Fill the area
        name=chart_name,             # Legend name
        text=new_df[aggregated_values_column],  # Text for the values
        textposition='top center'    # Position of the text labels
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        polar=dict(radialaxis=dict(visible=True)),
    )
    
    # Display the chart
    st.plotly_chart(fig)


def plot_wordcloud(text, title = "Word Cloud Example"):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Plot the Word Cloud
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")  # Remove axes

    # Display in Streamlit
    st.title(title)
    st.pyplot(fig)
    
def reset_data_in_session_state():
    datasets = ["df_radar", "df_3d_scatter", "df_timeline", "df_parallel", "df_density", "df_treemap", "df_funnel"
    "df_violin", "df_kde", "df_map", "df_sun", "df_bubble", "df_heat", "df_box", "df_area", "df_pie"
    "df_hbar", "df_hist", "df_scatter", "df_bar", "df_line"]

    for dataset in datasets:
        st.session_state[dataset] = None
        
    st.session_state["chart_idx"] = 0
    
    st.session_state.reload_data = True


if "reload_data" not in st.session_state:
    st.session_state.reload_data = False


        



    
streamlit_chart_map = {"area_chart": plot_area_chart, 
                     "bar_chart": plot_bar_chart, 
                     "box_plot": plot_box_plot,
                     "bubble_chart": plot_bubble_chart,
                     "heatmap": plot_heatmap,
                     "histogram": plot_histogram,
                     "kde_plot": plot_kde_plot,
                     "line_chart": plot_line_chart,
                     "pie_chart": plot_pie_chart,
                     "scatter_chart": plot_scatter_chart,
                     "violin_chart": plot_violin_chart,
                     "radar_chart": plot_radar_chart,
                     "3D_scatter_plot": plot_3D_scatter_plot,
                     "timeline_chart": plot_timeline_chart,
                     "parallel_coordinates": plot_parallel_coordinates,
                     "density_heatmap": plot_density_heatmap,
                     "treemap_chart": plot_treemap_chart,
                     "funnel_chart": plot_funnel_chart,
                     "choropleth_map": plot_choropleth_map,
                     "sunburst_chart": plot_sunburst_chart
                     }


if __name__ == "__main__":
    
    # Sample data for line chart
    df_line = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME'),
        'sales': np.random.randint(1000, 5000, size=12)
    })
    
    # Sample data for bar chart
    df_bar = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'values': np.random.randint(10, 50, size=4)
    })
    
    # Sample data for scatter chart
    df_scatter = pd.DataFrame({
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50)
    })
    
    # Sample data for histogram
    df_hist = pd.DataFrame({'age': np.random.randint(18, 65, size=100)})
    
    # Sample data for pie chart
    df_pie = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'count': np.random.randint(10, 30, size=3)
    })
    
    # Sample data for area chart
    df_area = df_line.copy()
    
    # Sample data for box plot
    df_box = pd.DataFrame({
        'group': np.random.choice(['A', 'B', 'C'], size=100),
        'values': np.random.randn(100)
    })
    
    # Sample data for heatmap
    df_heatmap = pd.DataFrame({
        'a_values': np.random.randint(0, 100, size=20),
        'b_values': np.random.randint(0, 100, size=20),
        'c_values': np.random.randint(0, 100, size=20),
        'x_values': np.random.randint(0, 100, size=20),
        'y_values': np.random.randint(0, 100, size=20),
        'z_values': np.random.randint(0, 100, size=20)
    })
    
    
    # Sample data for bubble chart
    df_bubble = pd.DataFrame({
        'x_col': np.random.randn(20),
        'y_col': np.random.randn(20),
        'size_col': np.random.randint(10, 50, size=20)
    })
    
    # Sample data for sunburst chart
    df_sunburst = pd.DataFrame({
        "categories": ["Earth", "Earth", "Earth", "Mars", "Mars", "Mars"],
        "regions": ["North America", "South America", "Europe", "North Pole", "South Pole", "Crater"],
        "populations": [500, 300, 200, 50, 25, 75],
    })
    
    
    # Sample data for kde plot
    df_kde = pd.Series(np.random.normal(loc=5, scale=2, size=1000))
    # df_kde = pd.DataFrame({
    #     "salary1": np.random.normal(loc=5, scale=2, size=1000),
    #     "salary2": np.random.normal(loc=5, scale=2, size=1000)
    #     }
    #     )
    
    # Sample data for map chart
    df_map = px.data.gapminder().query("year == 2007")
    
    # Sample data for violin plot
    df_violin = px.data.tips()
    
    # Sample data for Funnel chart
    df_funnel = pd.DataFrame({
        "Stage": ["Lead", "Qualified", "Proposal", "Negotiation", "Closed"],
        "Value": [1000, 800, 600, 400, 200]
    })
    
    # Sample data for treemap chart
    df_treemap = px.data.tips()
    
    
    # Sample data for Density Heatmap
    df_density = px.data.iris()
    
    
    # Sample data for parallel
    df_parallel = px.data.iris()
    
    
    # Sample data for timeline
    df_timeline = pd.DataFrame([
        dict(Task="Task 1", Start='2023-12-01', Finish='2023-12-05', Resource='Team A'),
        dict(Task="Task 2", Start='2023-12-03', Finish='2023-12-08', Resource='Team B'),
        dict(Task="Task 3", Start='2023-12-06', Finish='2023-12-10', Resource='Team A')
    ])
    
    
    # Sample data for 3D Scatter plot
    df_3d_scatter = px.data.iris()
    
    
    import plotly.graph_objects as go
    
    categories = ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency']
    
    values = [90, 80, 70, 85, 95]
    # Sample data for Radar chart
    df_radar = pd.DataFrame({"metrics": ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency'],
                  "values": [90, 80, 70, 85, 95]})
    
    
    
    # Sample data for word cloud
    word_cloud_text = """
    Data Science Machine Learning Artificial Intelligence Streamlit Python Cloud Computing 
    Visualization Automation Analysis Engineering Deep Learning Neural Networks NLP Computer Vision
    """
    
    
    
    
    # Example usage:
    # Assuming you have a DataFrame named 'data'
    plot_line_chart(df_line, 'date', 'sales', title = 'Sales Over Time')
    plot_bar_chart(df_bar, 'category', 'values', title = "Inventory Stock")
    plot_scatter_chart(df_scatter, 'feature1', 'feature2', title = 'Feature Correlation')
    plot_histogram(df_hist, 'age', title = 'Age Distribution')
    plot_hbar_chart(df_bar,'values', 'category', title = "Inventory Stock")
    plot_pie_chart(df_pie, 'count', 'category', title = 'Category Distribution')
    plot_area_chart(df_area, 'date', 'sales', title = 'Sales Volume Over Time')
    plot_box_plot(df_box, 'group', 'values', title = 'Group Distribution')
    plot_heatmap(df_heatmap, 'a_values', 'b_values', 'c_values', title = 'Correlation Heat Map')
    plot_bubble_chart(df_bubble, 'x_col', 'y_col', 'size_col', title = 'Size Bubble Chart')
    plot_sunburst_chart(df_sunburst, path = ["categories", "regions"], values = "populations", title = "Sunbursting Chart")
    plot_choropleth_map(df_map, "country", "iso_alpha", "gdpPercap", title = "GDP Per Capita")
    plot_kde_plot(df_kde, ["Data"], "kde", True, title = "KDE Plot")
    plot_violin_chart(df_violin, "day", "total_bill", "sex", title = "VIOLIN PLOT")
    plot_funnel_chart(df_funnel, "Value", "Stage", title = "Sales Funnel")
    plot_treemap_chart(df_treemap, ["day", "time"], "total_bill", "total_bill", title = "TreeMap for Total Bill for Meals")
    plot_density_heatmap(df_density, "sepal_width", "sepal_length", title = "Density Heatmap for Iris")
    plot_parallel_coordinates(df_parallel,
                              ["sepal_width", "sepal_length", "petal_width", "petal_length"],
                              "species_id", title = "Parallel Coordinates Example")
    plot_timeline_chart(df_timeline, "Start", "Finish", "Task", "Resource", title = "Timeline of Tasks")
    plot_3D_scatter_plot(df_3d_scatter, "sepal_length", "sepal_width","petal_width", "species", title = "3D Iris Scatterplot")
    plot_radar_chart(df_radar, "metrics", "values", title= "Visualizing Metrics")
    # plot_wordcloud(word_cloud_text)
