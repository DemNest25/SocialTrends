import os
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

# Usar DATABASE_URL de Render o local
POSTGRES_URL = os.environ.get("DATABASE_URL") or "postgresql+psycopg2://postgres:postgres@localhost:5432/socialtrends"
engine = create_engine(POSTGRES_URL)

def load_data():
    query = "SELECT keyword, created_at FROM tweets WHERE keyword IS NOT NULL"
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
    dcc.Graph(id="trend_chart"),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0)  # refresco cada minuto
])

# Callback para actualizar gráfico automáticamente
@app.callback(
    dash.dependencies.Output("trend_chart", "figure"),
    dash.dependencies.Input("interval", "n_intervals")
)
def update_chart(_):
    df = load_data()
    if df.empty:
        return px.line(title="No hay datos aún")
    
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
