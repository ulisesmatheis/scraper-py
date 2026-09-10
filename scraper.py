import pandas as pd
from jobspy import scrape_jobs
import os
import smtplib
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

# 4. Generar el cuerpo del correo en HTML (Blanco y Negro)
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: 'Segoe UI', Arial, sans-serif;
      background-color: #000000;
      color: #ffffff;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 650px;
      margin: 0 auto;
      background: #0a0a0a;
      border-radius: 4px;
      overflow: hidden;
      border: 1px solid #ffffff;
    }}
    .header {{
      background: #000000;
      color: #ffffff;
      padding: 25px 20px;
      text-align: center;
      border-bottom: 1px solid #ffffff;
    }}
    .header h2 {{
      margin: 0;
      font-size: 22px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .header p {{
      margin: 10px 0 0 0;
      font-size: 14px;
      color: #cccccc;
    }}
    .content {{
      padding: 25px 20px;
    }}
    .location-header {{
      color: #ffffff;
      border-bottom: 2px solid #ffffff;
      padding-bottom: 6px;
      margin-top: 30px;
      font-size: 16px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .location-header:first-child {{
      margin-top: 0;
    }}
    .job-card {{
      background: #121212;
      border: 1px solid #333333;
      border-left: 4px solid #ffffff;
      border-radius: 2px;
      padding: 16px;
      margin-bottom: 12px;
    }}
    .job-title {{
      margin: 0 0 8px 0;
      font-size: 16px;
    }}
    .job-title a {{
      color: #ffffff;
      text-decoration: underline;
      font-weight: 600;
    }}
    .job-detail {{
      margin: 4px 0;
      font-size: 13px;
      color: #cccccc;
    }}
    .footer {{
      background: #000000;
      color: #888888;
      text-align: center;
      padding: 20px;
      font-size: 11px;
      line-height: 1.5;
      border-top: 1px solid #333333;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Reporte de Vacantes</h2>
      <p>Se encontraron <strong>{len(todas_las_vacantes)}</strong> publicaciones en las ultimas {horas} horas</p>
    </div>
    <div class="content">
"""

# Agrupar vacantes por ubicación
vacantes_por_ubicacion = todas_las_vacantes.groupby('location')

for location, group in vacantes_por_ubicacion:
    html_content += f"<h3 class='location-header'>{location}</h3>"
    
    for index, row in group.iterrows():
        html_content += f"""
        <div class="job-card">
            <h4 class="job-title"><a href="{row['job_url']}" target="_blank">{row['title']}</a></h4>
            <p class="job-detail"><strong>Empresa:</strong> {row['company']}</p>
        </div>
        """

html_content += """
    </div>
    <div class="footer">
      <p>El archivo adjunto contiene la lista completa en formato CSV.</p>
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

msg['Subject'] = "Alerta Automatica: Nuevas Vacantes de Data y Dev"
msg.attach(MIMEText(html_content, 'html'))

# Adjuntar archivo CSV
try:
    with open(archivo_csv, "rb") as f:
        adjunto = MIMEApplication(f.read(), _subtype="csv")
        adjunto.add_header('Content-Disposition', 'attachment', filename=archivo_csv)
        msg.attach(adjunto)
except FileNotFoundError:
    print("Archivo CSV no encontrado para adjuntar.")

# Enviar correo mediante SMTP
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(remitente, password)
    server.send_message(msg)
    server.quit()
    print("Correo enviado exitosamente.")
except Exception as e:
    print(f"Error al enviar correo: {e}")
