import pandas as pd
from jobspy import scrape_jobs

# Ejecución de la búsqueda
jobs = scrape_jobs(
    site_name=["linkedin"],
    search_term="Data Analyst",
    location="Mexico",
    results_wanted=15,
    hours_old=24
)

# Exportar resultados a CSV
jobs.to_csv("vacantes.csv", index=False)
