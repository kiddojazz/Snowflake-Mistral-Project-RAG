# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 04:17:40 2025

@author: olanr
"""


import sys
sys.path.append("..")
from pydantic import BaseModel
from typing import Dict, Union, List, Optional
from enum import Enum


class ReportDescription(BaseModel):
    report_name: str
    description: str
    
class NumReports(BaseModel):
    reports: List[ReportDescription]
    num_reports: int 

class SqlQuery(BaseModel):
    output: str
    
class ChartStep(BaseModel):
    chart_type: str
    chart_description: str
    chart_title: str
    chart_columns: Dict[str, str]

class GenerateCharts(BaseModel):
    chart_content: List[ChartStep]



class ContextTexts(Enum):
    
    TABLE_DESCRIPTION = """I have an SQL Server Table called {table_name}. The table has the following columns:
        {table_columns}
        
        These columns have sample values given below:
            {sample_column_values}
            
        """
        
    GET_SQL_FROM_PROMPT = """Help return an SQL Query that can answer the prompt: {user_prompt}. 
        Use the SQL Server Table Description given below as a guide:
        Table Description:
           {table_description}
        
        """
        
    GET_NUM_REPORTS = """Help return the number of relevant detailed reports (from 1 to 3) that can be used to answer
    the user prompt: '{user_prompt}'.

    Return your answer **only** as a valid JSON object. Do **not** include any explanations, comments, or text outside the JSON object.

    The JSON object must strictly follow the schema below:
    {output_format}
    If your output does not strictly match the JSON schema, it will fail validation.
    Ensure your output strictly adheres to the following JSON schema:


    The reports are going to be generated using SQL queries from the SQL Server table described below:
    Table Description:
    {table_description}



    """
    
    GET_SQL_FROM_DESCRIPTION = """Help answer the user query by returning an SQL Query in valid JSON. 
    1. Please keep in mind that the resulting table of the SQL query will be used to create charts and graphs
    2. This SQL Query must answer the report statement and report description provided below.
    3. The SQL Query must be able to query an Snowflake Database Table whose description is also given below
    4. Make sure the SQL Query is valid SQL Server Query.
    5. You can make use of CTE's or Subqueries, depending on the complexity of the scenario
    6. Return your answer **only** as a valid JSON object. Do **not** include any explanations, comments, or text outside the JSON object.
    7. The JSON object must strictly follow the schema below:
    {output_format}
    8. Do NOT add any backslash or any unnecessary character. I don't care about neat or orderly formatting.
    
    Report Statement: {report_statement}
    Report Description: {report_description}
    
    SQL Server Table Description:
        {table_description}

    **Expected Output**:
    'output': '<SQL_Query''
    """

    
    GET_CHART_SUMMARY = """Determine the appropriate charts and graphs to answer the user's prompt.

    1. **Instructions**:
        - Do **not** generate charts; instead, provide detailed instructions for chart creation.
        - Return the response **only** as a valid JSON object following the schema: {output_format}.
        - Each Chart can only take ONE x-axis column and ONE y-axis column. DO NOT in any circumstance provide multiple column values for x-axis or y-axis columns.
        - **Chart Type**: Specify the chart type (e.g., bar_chart, line_chart, etc.).
        - **Description**: Briefly describe the chart and the data it represents.
        - **Chart Title**: Provide a clear, descriptive title.
        - **Chart Columns**: 
            - Map the dataset columns to the chart x and y-axes (e.g., "x_col": "column1", "y_col": "column2"). 
            - `x_col` and `y_col` **must be single column names** from the dataset (no lists or arrays). 
        - Do NOT add backslashes, comments, or extra characters.

    2. **Inputs**:
        - **User Prompt**: `{user_prompt}`
        - **Dataset Mapping**: `{df_map}`
        - **Dataset Stats**: `{df_stats}`
        - **Chart Types**: `{chart_names}`
        - **Chart Metadata**: `{chart_map}`

    3. **Output**:
        - **Chart Type**: [Description, Title]
        - **Chart Columns**


            """



class LoadTableInfo:
    
    _table_to_col_map = {
        "MISTRALHEALTHDB.MEDICALRECORDDATAMART.FLATTENED_MEDICAL_RECORDS":[
            (
            'record_id', 'heart_rate', 'blood_pressure', 'temperature',
            'respiratory_rate', 'oxygen_saturation', 'created_at',
            'patient_id', 'patient_name', 'date_of_birth',
            'age', 'gender', 'blood_type',
            'diagnosis', 'treatment_plan', 'medication', 'allergies',
            'insurance_provider', 'insurance_id', 'attending_physician', 'department', 'device_id',
            'admission_date', 'discharge_date', 'last_updated_at'
           ), 
            
            ('39585f0c-555b-4f2d-9c2c-b23c6e6cdf19', "Integer('99')", 
             "99/68", "Decimal('36.5')", "Integer('16')", "Integer('98')", 
             '2025-01-16 15:21:09', '80e98385-690f-41fb-9538-272061014b59', 'Cristina Henry', '1950-07-19', 
             '76', 'Female', 'A+', "Hypertension", 
             'Control manage think down', 'Metformin, Ibuprofen', '', 'UnitedHealth', "Dkd-77564713", 
             'Christopher Johnson, MD', "Oncology", 
             '2025-01-06 02:11:16', '2025-01-16 15:21:09', 
             '2025-01-16 15:21:09',)
            
            ]
                        }
    
    default_table_name = "MISTRALHEALTHDB.MEDICALRECORDDATAMART.FLATTENED_MEDICAL_RECORDS"
    
    def __init__(self, table_name):
        self.table_name = table_name
        
    
    def get_table_col_map(self):
        return self._table_to_col_map
    
    def load_info(self):
        table_col_map = self.get_table_col_map()
        return table_col_map[self.table_name]
    

class ChartReference:
    
    chart_map = {"line_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a line chart using the specified columns from the dataframe. 'title' gives the name header on the chart"""],
                 "bar_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a bar chart using the specified columns from the dataframe. 'title' gives the name header on the chart"""],
                 "scatter_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a scatter chart using the specified columns from the dataframe, and 'title' gives the name header on the chart"""],
                 "histogram": ["df: pd.DataFrame", "col: str", "title: str", """Plots a histogram for the specified column of the dataframe. 'title' gives the name header on the chart"""],
                 "pie_chart": ["df: pd.DataFrame", "values: str", "names: str", "title: str", """Plots a pie chart for the distribution of values in a specified column. 'title' gives the name header on the chart"""],
                 "area_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots an area chart based on cumulative values from the dataframe.   and 'title' gives the name header on the chart"""],
                 "box_plot": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a box plot to show the distribution of values in one column grouped by another column.   and 'title' gives the name header on the chart"""],
                 "heatmap": ["df: pd.DataFrame", "x_col: str", "y_col: str", "values: str", "title: str", """Plots a heatmap of the correlation matrix of numerical columns in the dataframe.   and 'title' gives the name header on the chart"""],
                 "bubble_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "size_col: str", "image_filename:str", "title: str", """Plots a bubble chart, where the size of the bubbles is determined by a specified column.   and 'title' gives the name header on the chart"""],
                 "sunburst_chart": ["df: pd.DataFrame", "path: List", "values: str", "title: str", """Plots a sunburst chart, with path being a list of columns within the dataset and 'title' gives the name header on the chart"""],
                 "choropleth_map": ["df: pd.DataFrame", "hover_column: str", "location_column: str", "color_column: str", "title: str", """Plots a choropleth map, where the size of the bubbles is determined by a specified column.'title' gives the name header on the chart"""],
                 "kde_plot": ["df: Union[pd.DataFrame, pd.Series]", "x_col: str", "group_labels: List", """Plots a Kernel Density Estimate (KDE) plot to estimate the probability density of a continuous variable. group_labels argument gives the name of the kde plot for a pandas series. If a pandas dataframe is passed, """],
                 "violin_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "color_col: str", "title: str", """Plots a violin chart to show the distribution of data for different categories.   and 'title' gives the name header on the chart"""],
                 "funnel_chart": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a funnel chart using the provided data. 'title' gives the name header on the chart"""],
                 "treemap_chart": ["df: pd.DataFrame", "path: List", "values_col: str", "color_col: str", "title: str", """Plots a treemap chart using the provided data. The 'path' argument is a list of categorical columns, 'title' gives the name header on the chart"""],
                 "density_heatmap": ["df: pd.DataFrame", "x_col: str", "y_col: str", "title: str", """Plots a density heatmap using the provided data. 'title' gives the name header on the chart"""],
                 "parallel_coordinates": ["df: pd.DataFrame", "dimensions: List", "color_col: str", "title: str", """Plots a parallel coordinates using the provided data. 'title' gives the name header on the chart"""],
                 "timeline_chart": ["df: pd.DataFrame", "x_start: str", "x_end: str", "y_col: str", "color_col: str", "title: str", """Plots a parallel coordinates using the provided data. The 'dimension' argument is a list of numeric columns, 'title' gives the name header on the chart"""],
                 "3D_scatter_plot": ["df: pd.DataFrame", "x_col: str", "y_col: str", "z_col: str", "color_col: str", "title: str", """Plots a 3D scatter plot using the provided data. 'title' gives the name header on the chart"""],
                 "radar_chart": ["df: pd.DataFrame", "unique_col: str", "aggregated_column: str", "chart_name: str", "color_col: str", "title: str", """Plots a radar chart using the provided data. 'title' gives the name header on the chart"""],
                 #"wordcloud": ["text: str", "title: str", """Plots a word cloud using the provided data. 'title' gives the name header on the chart"""]
                 
                 }
    
    chart_description_map = {"bar_chart": """Plots a bar chart using the specified columns from the dataframe. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted on the x-axis. y_col (str): The name of the column to be plotted on the y-axis. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the bar chart with annotated values on top of bars.""",
                 "line_chart": """Plots a line chart using the specified columns from the dataframe. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted on the x-axis. y_col (str): The name of the column to be plotted on the y-axis. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the line chart.""",
                 "scatter_chart": """Plots a scatter chart using the specified columns from the dataframe, with optional hue coloring. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted on the x-axis. y_col (str): The name of the column to be plotted on the y-axis. hue_col (str): The column used for coloring the points based on categories. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the scatter plot.""",
                 "histogram": """Plots a histogram for the specified column of the dataframe. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted in the histogram. image_filename (str): The filename to save the plot as an image. bins (int, optional): The number of bins to be used in the histogram. Default is 10. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the histogram with annotated bar heights.""",
                 "pie_chart": """Plots a pie chart for the distribution of values in a specified column. Parameters: df (pd.DataFrame): The dataframe containing the data. pie_col (str): The column for which the pie chart is to be plotted. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the pie chart.""",
                 "area_chart": """Plots an area chart based on cumulative values from the dataframe. Parameters: df (pd.DataFrame): The dataframe containing the data. category_col (str): The column used for grouping data in the area chart. value_col (str): The column for the values to be plotted. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the area chart.""",
                 "box_plot": """Plots a box plot to show the distribution of values in one column grouped by another column. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column for categorical grouping. y_col (str): The name of the column to be plotted on the y-axis. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the box plot with calculated statistics annotated.""",
                 "heatmap": """Plots a heatmap of the correlation matrix of numerical columns in the dataframe. Parameters: df (pd.DataFrame): The dataframe containing the data. non_numeric_cols (List): List of non-numeric column names to exclude from the correlation matrix. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the heatmap.""",
                 "bubble_chart": """Plots a bubble chart, where the size of the bubbles is determined by a specified column. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted on the x-axis. y_col (str): The name of the column to be plotted on the y-axis. size_col (str): The name of the column used to determine the size of the bubbles. hue_col (str): The column used for coloring the bubbles based on categories. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the bubble chart.""",
                 "kde_plot": """Plots a Kernel Density Estimate (KDE) plot to estimate the probability density of a continuous variable. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The name of the column to be plotted on the x-axis. hue_col (str): The column used for differentiating groups in the KDE plot. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the KDE plot.""",
                 "violin_chart": """Plots a violin chart to show the distribution of data for different categories. Parameters: df (pd.DataFrame): The dataframe containing the data. x_col (str): The column to be plotted on the x-axis. y_col (str): The column to be plotted on the y-axis. image_filename (str): The filename to save the plot as an image. title (str, optional): The title of the plot. Default is an empty string. Returns: None: Displays and saves the violin plot."""
                 }
    
    
    def __init__(self, chart_name: Union[str, None] = None):
        self._chart_name = chart_name if chart_name else None
        
    
    def load_map(self):
        return self.chart_map
    
    def load_description(self):
        return self.chart_description_map
    
    def select_map(self):
        if self._chart_name:
            return self.chart_map[self._chart_name]
        raise ValueError("Chart Name not specified")
        
    def load_chart_names(self):
        return list(self.chart_map.keys())
        
