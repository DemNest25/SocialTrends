import os
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

# Usar DATABASE_URL de Render
POSTGRES_URL = os.environ.get("DATABASE_URL")
engine = create_engine(POSTGRES_URL)

def load_data():
    query = "SELECT keyword, created_at FROM tweets"
    df = pd.read_sql(query, engine)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    return df

# Crear app Dash
app = dash.Dash(__name__)
server = app.server  # necesario para Gunicorn en Render

# Layout
app.layout = html.Div([
    html.H1("📈 Tendencias en X (Twitter)"),
    dcc.Dropdown(id="keyword_selector", multi=True, placeholder="Selecciona keywords"),
    dcc.Graph(id="trend_chart"),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0)  # refresco cada minuto
])

# Callback para actualizar keywords
@app.callback(
    dash.dependencies.Output("keyword_selector", "options"),
    dash.dependencies.Output("keyword_selector", "value"),
    dash.dependencies.Input("interval", "n_intervals")
)
def update_keywords(_):
    df = load_data()
    if df.empty:
        return [], []
    keywords = df["keyword"].unique()
    options = [{"label": k, "value": k} for k in keywords]
    return options, list(keywords)

# Callback para actualizar gráfico
@app.callback(
    dash.dependencies.Output("trend_chart", "figure"),
    dash.dependencies.Input("keyword_selector", "value"),
    dash.dependencies.Input("interval", "n_intervals")
)
def update_chart(selected_keywords, _):
    df = load_data()
    if df.empty or not selected_keywords:
        return px.line()  # gráfico vacío
    df = df[df["keyword"].isin(selected_keywords)]
    df_grouped = df.groupby(["date", "keyword"]).size().reset_index(name="count")
    fig = px.line(
        df_grouped,
        x="date",
        y="count",
        color="keyword",
        title="Tendencia de tweets por keyword"
    )
    return fig

# Bloque para pruebas locales
if __name__ == "__main__":
    app.run_server(debug=True)
