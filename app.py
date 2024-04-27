import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import jupyter_dash
from dash import html, Dash, dcc
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = """  
According to analysis conducted by the Pew Research Center in 2023, the gender wage gap has remained fairly steady over the last two decades, whereby women tend to earn approximately 80 percent of what men do on average.  Their work did add some nuance to the discrepancy by highlighting that the gap has narrowed for workers between 25 and 34; while men on average make more, in that age range the gap is closer to an 8 rather than 18 percent (https://www.pewresearch.org/short-reads/2023/03/01/gender-pay-gap-facts/).  A 2023 report from the U.S. Department of Labor explored the causes of the delta in pay and had some interesting findings.  Their analysis indicated that, while some of the pay differences could be attributed to factors like education, age, or work hours, about 70 percent of the instances of differential pay were unexplained, at least some of which is related to discrimination (https://www.dol.gov/sites/dolgov/files/WB/equalpay/WB_issuebrief-undstg-wage-gap-v1.pdf).

Since 1972, the General Social Survey (GSS) has been conducted by the National Opinion Research Center (NORC) at the University of Chicago.  It includes a variety demographic, behavioral, and attitudinal questions, as well as topics of special interest and has the goal to monitor and explain trends in opinions, attitudes and behaviors in American society, (https://gss.norc.org/About-The-GSS).  
"""

gss_prob2 = gss_clean.groupby('sex').agg({'income': 'mean', 'job_prestige':'mean',
                                    'socioeconomic_index':'mean', 'education': 'mean'}).reset_index()

table = ff.create_table(gss_prob2)
table.update_layout(autosize=True)

fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', color='sex',
                 trendline='ols',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])     

fig_box_income = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Income', 'sex':''})
fig_box_income.update_layout(showlegend=False)

fig_box_prestige = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Occupational Prestige', 'sex':''})
fig_box_prestige.update_layout(showlegend=False)

gss_6 = gss_clean[['income', 'sex', 'job_prestige']]
gss_6['job_prestige_category'] = pd.cut(gss_6['job_prestige'], bins=6)
gss_6 = gss_6.dropna()
gss_6['job_prestige_category'] = pd.Categorical(gss_6['job_prestige_category'], categories=sorted(gss_6['job_prestige_category'].unique()), ordered=True)
gss_6 = gss_6.sort_values(by='job_prestige_category')

fig_box_facet = px.box(gss_6, x='income', y='sex', color='sex', 
             facet_col='job_prestige_category', facet_col_wrap=2,
             height=900, width=800,
             labels={'income':'Income', 'sex':'Gender'},
             color_discrete_map = {'male':'blue', 'female':'pink'})
fig_box_facet.for_each_annotation(lambda a: a.update(text=a.text.replace("job_prestige_category=", "Job Prestige Range ")))

import dash_bootstrap_components as dbc

ft_columns = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork'] 
cat_columns = ['sex', 'region', 'education']

app3 = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE], meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],)

app3.layout = html.Div(
    [
        html.H1("Exploring the American Gender Income Gap"),
        dcc.Markdown(children=markdown_text),
        dcc.Tabs([
            dcc.Tab(label='Average Metrics by Gender', children=[
                html.H2("Average Income, Occupational Prestige, Education, and Socioeconomic Index by Gender"),
                dcc.Graph(figure=table),
            ]),
            dcc.Tab(label='Opinions on Gender Work Roles', children=[
                html.H2("Opinions Regarding Traditional Gender Work Roles"),
                html.Div([
                    html.H3("x-axis feature"),
                    dcc.Dropdown(
                        id='x-axis',
                        options=[{'label': i, 'value': i} for i in ft_columns],
                        value='male_breadwinner'
                    ),
                    html.H3("colors"),
                    dcc.Dropdown(
                        id='color',
                        options=[{'label': i, 'value': i} for i in cat_columns],
                        value='sex'
                    ),
                    html.Div([
                        dcc.Graph(id="graph")
                    ])
                ])  
            ]),  
            dcc.Tab(label='Income by Occupational Prestige', children=[
                html.H2("Male and Female Income By Occupational Prestige"),
                dcc.Graph(figure=fig_scatter),
            ]),
            dcc.Tab(label='Distribution of Incomes By Gender', children=[
                html.H2("Male and Female Income"),
                dcc.Graph(figure=fig_box_income),
            ]),
            dcc.Tab(label='Distribution of Occupational Prestige By Gender', children=[
                html.H2("Male and Female Occupational Prestige"),
                dcc.Graph(figure=fig_box_prestige),
            ]),
            dcc.Tab(label='Sub-Categories of Occupational Prestige by Gender', children=[
                html.H2("Exploring Sub-categories of Occupational Prestige by Gender"),
                dcc.Graph(figure=fig_box_facet)
            ])
        ], content_style={'height': '300px', 'overflowY': 'auto'})
    ]
)

@app3.callback(Output(component_id="graph", component_property="figure"), 
              [Input(component_id='x-axis', component_property="value"),
               Input(component_id='color', component_property="value")])
def make_figure(x, color):
    gss_prob3 = pd.crosstab(gss_clean[x], gss_clean[color]).reset_index()
    gss_3_melt = pd.melt(gss_prob3, id_vars=x)
    fig = px.bar(gss_3_melt, x=x, y='value', color=color, hover_data=[x, 'value', color], barmode='group')   
    return fig

if __name__ == '__main__':
    app3.run_server(debug=True, port=8051, host='0.0.0.0')
