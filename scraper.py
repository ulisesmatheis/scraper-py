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
jobs_analyst_cdmx = scrape_jobs(site_name=sitios, search_term="Data Analyst", location="Ciudad de México, Mexico", results_wanted=resultados, hours_old=horas, country_indeed=pais_indeed)
jobs_engineer_cdmx = scrape_jobs(site_name=sitios, search_term="Data Engineer", location="Ciudad de México, Mexico", results_wanted=resultados, hours_old=horas, country_indeed=pais_indeed)
jobs_fullstack_mty = scrape_jobs(site_name=sitios, search_term="Desarrollador Fullstack", location="Monterrey, Mexico", results_wanted=resultados, hours_old=horas, country_indeed=pais_indeed)

# 3. Limpieza y exportación
todas_las_vacantes = pd.concat([jobs_analyst_cdmx, jobs_engineer_cdmx, jobs_fullstack_mty], ignore_index=True)
todas_las_vacantes = todas_las_vacantes.drop_duplicates(subset=['title', 'company', 'location']).fillna("No especificado")
archivo_csv = "vacantes_combinadas.csv"
todas_las_vacantes.to_csv(archivo_csv, index=False)

# 4. Generar el cuerpo del correo en HTML con diseño moderno
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
    .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .header {{ background: #2c3e50; color: #ffffff; padding: 25px 20px; text-align: center; }}
    .header h2 {{ margin: 0; font-size: 24px; letter-spacing: 0.5px; }}
    .header p {{ margin: 10px 0 0 0; font-size: 15px; color: #bdc3c7; }}
    .content {{ padding: 30px 20px; }}
    .location-header {{ color: #2980b9; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; margin-top: 30px; font-size: 20px; }}
    .location-header:first-child {{ margin-top: 0; }}
    .job-card {{ background: #ffffff; border: 1px solid #e1e8ed; border-radius: 6px; padding: 18px; margin-bottom: 15px; border-left: 5px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
    .job-title {{ margin: 0 0 10px 0; font-size: 18px; }}
    .job-title a {{ color: #2c3e50; text-decoration: none; font-weight: 600; }}
    .job-title a:hover {{ color: #3498db; text-decoration: underline; }}
    .job-detail {{ margin: 5px 0; font-size: 14px; color: #555; }}
    .footer {{ background: #ecf0f1; color: #7f8c8d; text-align: center; padding: 20px; font-size: 12px; line-height: 1.5; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Oportunidades Laborales</h2>
      <p>Se encontraron <strong>{len(todas_las_vacantes)}</strong> nuevas vacantes en las últimas {horas} horas</p>
    </div>
    <div class="content">
"""

# Agrupar vacantes por ubicación usando Pandas
vacantes_por_ubicacion = todas_las_vacantes.groupby('location')

for location, group in vacantes_por_ubicacion:
    html_content += f"<h3 class='location-header'>📍 {location}</h3>"
    
    for index, row in group.iterrows():
        html_content += f"""
        <div class="job-card">
            <h4 class="job-title"><a href="{row['job_url']}" target="_blank">{row['title']}</a></h4>
            <p class="job-detail"><strong>🏢 Empresa:</strong> {row['company']}</p>
        </div>
        """

html_content += """
    </div>
    <div class="footer">
      <p>El reporte detallado se encuentra adjunto en formato CSV.</p>
      <p><strong>Por favor, no respondas a este correo.</strong><br>Este es un mensaje automatizado generado y enviado mediante GitHub Actions.</p>
    </div>
  </div>
</body>
</html>
"""

# 5. Configurar y enviar el correo
remitente = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
destinatario = os.environ.get('MAIL_DESTINO')

msg = MIMEMultipart()
msg['From'] = remitente
msg['To'] = destinatario
msg['Subject'] = "🚀 Alerta Automática: Nuevas Vacantes de Data & Dev"
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
