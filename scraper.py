import pandas as pd
from jobspy import scrape_jobs

# Parámetros compartidos
sitios = ["linkedin", "indeed"]
horas = 72 # 3 días (24 * 3)
pais_indeed = "mexico"
resultados_por_busqueda = 15

# 1. Búsqueda CDMX: Data Analyst
jobs_analyst_cdmx = scrape_jobs(
    site_name=sitios,
    search_term="Data Analyst",
    location="Ciudad de México, Mexico",
    results_wanted=resultados_por_busqueda,
    hours_old=horas,
    country_indeed=pais_indeed
)

# 2. Búsqueda CDMX: Data Engineer
jobs_engineer_cdmx = scrape_jobs(
    site_name=sitios,
    search_term="Data Engineer",
    location="Ciudad de México, Mexico",
    results_wanted=resultados_por_busqueda,
    hours_old=horas,
    country_indeed=pais_indeed
)

# 3. Búsqueda Monterrey: Desarrollador Fullstack
jobs_fullstack_mty = scrape_jobs(
    site_name=sitios,
    search_term="Desarrollador Fullstack",
    location="Monterrey, Mexico",
    results_wanted=resultados_por_busqueda,
    hours_old=horas,
    country_indeed=pais_indeed
)

# Unir los tres resultados en una sola tabla
todas_las_vacantes = pd.concat(
    [jobs_analyst_cdmx, jobs_engineer_cdmx, jobs_fullstack_mty], 
    ignore_index=True
)

# Opcional: Eliminar vacantes duplicadas (ej. si la misma empresa publicó en LinkedIn e Indeed)
todas_las_vacantes = todas_las_vacantes.drop_duplicates(subset=['title', 'company', 'location'])

# Exportar a un solo archivo CSV
todas_las_vacantes.to_csv("vacantes_combinadas.csv", index=False)
print(f"Proceso finalizado. Se encontraron {len(todas_las_vacantes)} vacantes únicas.")
