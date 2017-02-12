import json
import requests
from requests.auth import HTTPBasicAuth

headers = {'Plotly-Client-Platform': 'python'}

with open('./config.json') as config_file:
    plotlyuserconf = json.load(config_file)

auth = HTTPBasicAuth(plotlyuserconf['plotly_username'],
                     plotlyuserconf['plotly_api_key'])

#payload = {
#    'figure': {'data': [{'marker': {'color': 'rgb(227, 119, 194)'},
#    'type': 'bar',
#    'xsrc': 'subnivean:11:2c8057',
#    'ysrc': 'subnivean:11:465676'}]},
#    'world_readable': 'true'
#}

payload = {'figure':
{
  "data": [
    {
      "name": "CSPH (F)",
      "xsrc": "subnivean:21:17606b",
      "ysrc": "subnivean:21:dd1f42",
      "mode": "lines+markers",
      "type": "scatter"
    }
  ],
  "layout": {
    "autosize": "true",
    "title": "Current CSPH temperature",
    "showlegend": "true",
    "height": 566,
    "width": 803,
    "titlefont": {
      "color": "#444",
      "family": "\"Open sans\", verdana, arial, sans-serif",
      "size": 17
    },
    "font": {
      "color": "#444",
      "family": "\"Open sans\", verdana, arial, sans-serif",
      "size": 12
    },
    "legend": {
      "bordercolor": "#444",
      "yanchor": "auto",
      "traceorder": "normal",
      "xanchor": "left",
      "bgcolor": "rgba(255, 255, 255, 0.5)",
      "borderwidth": 0,
      "y": 1.02,
      "x": 1,
      "font": {
        "color": "#444",
        "family": "\"Open sans\", verdana, arial, sans-serif",
        "size": 12
      }
    }
  }
}
}

r = requests.post('https://api.plot.ly/v2/plots',
                  auth=auth, headers=headers, json=payload)
print r.text

#rows = {"rows": [['x', 4], ['y', 1], ['z', 3]]}
#
#r = requests.post('https://api.plot.ly/v2/grids/subnivean:7/row',
#                  auth=auth, headers=headers, json=rows)
#
#print r.status_code
