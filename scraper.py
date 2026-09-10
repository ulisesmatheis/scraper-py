import pandas as pd
from jobspy import scrape_jobs
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# 1. Parámetros de búsqueda
sitios = ["linkedin", "indeed"]
horas = 72
pais_indeed = "mexico"
resultados = 15

# 2. Ejecutar extracciones
jobs_analyst_cdmx = scrape_jobs(
    site_name=sitios,
    search_term="Data Analyst",
    location="Ciudad de México, Mexico",
    results_wanted=resultados,
    hours_old=horas,
    country_indeed=pais_indeed
)
jobs_engineer_cdmx = scrape_jobs(
    site_name=sitios,
    search_term="Data Engineer",
    location="Ciudad de México, Mexico",
    results_wanted=resultados,
    hours_old=horas,
    country_indeed=pais_indeed
)
jobs_fullstack_mty = scrape_jobs(
    site_name=sitios,
    search_term="Desarrollador Fullstack",
    location="Monterrey, Mexico",
    results_wanted=resultados,
    hours_old=horas,
    country_indeed=pais_indeed
)

# 3. Limpieza y exportación
todas_las_vacantes = pd.concat([jobs_analyst_cdmx, jobs_engineer_cdmx, jobs_fullstack_mty], ignore_index=True)
todas_las_vacantes = todas_las_vacantes.drop_duplicates(subset=['title', 'company', 'location']).fillna("No especificado")
archivo_csv = "vacantes_combinadas.csv"
todas_las_vacantes.to_csv(archivo_csv, index=False)

# Obtener fecha actual para el asunto y reporte
fecha_envio = datetime.now().strftime("%d/%m/%Y")

# 4. Generar el cuerpo del correo en HTML (Estilo Mercado Libre)
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f5f5f5;
      color: #333333;
      margin: 0;
      padding: 30px 10px;
    }}
    .container {{
      max-width: 580px;
      margin: 0 auto;
    }}
    .top-bar {{
      display: table;
      width: 100%;
      margin-bottom: 12px;
      font-size: 11px;
      color: #8c8c8c;
      letter-spacing: 0.5px;
    }}
    .top-title {{
      display: table-cell;
      text-align: left;
      font-weight: 700;
      color: #333333;
      text-transform: uppercase;
    }}
    .top-id {{
      display: table-cell;
      text-align: right;
      vertical-align: middle;
    }}
    .status-card {{
      background-color: #ffffff;
      border: 1px solid #e6e6e6;
      border-left: 4px solid #00a650;
      border-radius: 6px;
      padding: 18px 20px;
      margin-bottom: 14px;
    }}
    .status-title {{
      font-size: 16px;
      font-weight: 700;
      color: #222222;
      margin: 0 0 4px 0;
    }}
    .status-subtitle {{
      font-size: 14px;
      color: #666666;
      margin: 0;
    }}
    .main-card {{
      background-color: #ffffff;
      border: 1px solid #e6e6e6;
      border-radius: 6px;
      padding: 24px 20px;
      margin-bottom: 20px;
    }}
    .section-header {{
      font-size: 15px;
      font-weight: 700;
      color: #222222;
      margin: 0 0 15px 0;
    }}
    .location-title {{
      font-size: 13px;
      font-weight: 700;
      color: #3483fa;
      margin: 22px 0 10px 0;
      padding-bottom: 6px;
      border-bottom: 1px solid #eeeeee;
      text-transform: uppercase;
    }}
    .location-title:first-of-type {{
      margin-top: 5px;
    }}
    .job-item {{
      padding: 14px 0;
      border-bottom: 1px solid #f2f2f2;
    }}
    .job-item:last-child {{
      border-bottom: none;
    }}
    .job-name {{
      font-size: 15px;
      font-weight: 600;
      color: #222222;
      margin: 0 0 4px 0;
    }}
    .job-company {{
      font-size: 13px;
      color: #666666;
      margin: 0 0 3px 0;
    }}
    .job-date {{
      font-size: 12px;
      color: #8c8c8c;
      margin: 0 0 12px 0;
    }}
    .btn-link {{
      display: inline-block;
      background-color: #3483fa;
      color: #ffffff !important;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      padding: 9px 20px;
      border-radius: 6px;
    }}
    .footer {{
      text-align: center;
      font-size: 12px;
      color: #999999;
      line-height: 1.6;
      margin-top: 25px;
    }}
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Encabezado superior -->
    <div class="top-bar">
      <div class="top-title">REPORTE DE VACANTES</div>
      <div class="top-id">GITHUB ACTIONS</div>
    </div>

    <!-- Tarjeta de estado (Borde verde) -->
    <div class="status-card">
      <p class="status-title">Nuevas vacantes encontradas</p>
      <p class="status-subtitle">Se detectaron <strong>{len(todas_las_vacantes)}</strong> ofertas en las ultimas {horas} horas.</p>
    </div>

    <!-- Tarjeta principal -->
    <div class="main-card">
      <p class="section-header">Detalle del reporte ({fecha_envio}):</p>
"""

# Agrupar vacantes por ubicación
vacantes_por_ubicacion = todas_las_vacantes.groupby('location')

for location, group in vacantes_por_ubicacion:
    html_content += f'<div class="location-title">Ubicacion: {location}</div>'
    for index, row in group.iterrows():
        fecha_publicacion = row.get('date_posted', 'No especificada')
        html_content += f"""
        <div class="job-item">
          <p class="job-name">{row['title']}</p>
          <p class="job-company">Empresa: {row['company']}</p>
          <p class="job-date">Fecha de publicacion: {fecha_publicacion}</p>
          <a href="{row['job_url']}" class="btn-link" target="_blank">Ver oferta</a>
        </div>
        """

html_content += """
    </div>

    <!-- Pie de pagina -->
    <div class="footer">
      <p>El reporte detallado se encuentra adjunto en formato CSV.</p>
      <p><strong>Por favor no respondas a este correo.</strong><br>Este es un mensaje automatico generado y enviado mediante GitHub Actions.</p>
    </div>

  </div>
</body>
</html>
"""

# 5. Configurar y enviar el correo
remitente = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
destinatario = os.environ.get('MAIL_DESTINO')
cc_destinatario = os.environ.get('MAIL_CC')

msg = MIMEMultipart()
msg['From'] = remitente
msg['To'] = destinatario

if cc_destinatario:
    msg['Cc'] = cc_destinatario

msg['Subject'] = f"Reporte de Vacantes: Data y Desarrollador Fullstack - {fecha_envio}"
msg.attach(MIMEText(html_content, 'html'))

# Adjuntar el CSV
try:
    with open(archivo_csv, "rb") as f:
        adjunto = MIMEApplication(f.read(), _subtype="csv")
        adjunto.add_header('Content-Disposition', 'attachment', filename=archivo_csv)
        msg.attach(adjunto)
except FileNotFoundError:
    print("Archivo CSV no encontrado para adjuntar.")

# Conexión al servidor SMTP
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(remitente, password)
    server.send_message(msg)
    server.quit()
    print("Correo enviado exitosamente.")
except Exception as e:
    print(f"Error al enviar correo: {e}")
