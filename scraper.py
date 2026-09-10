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

# 4. Generar el cuerpo del correo en HTML
html_content = """
<html>
  <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Reporte Automatizado de Vacantes</h2>
    <p>Se han encontrado <strong>{}</strong> nuevas oportunidades laborales en las últimas 72 horas:</p>
""".format(len(todas_las_vacantes))

for index, row in todas_las_vacantes.iterrows():
    html_content += f"""
    <div style="background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 5px; border-left: 4px solid #3498db;">
        <h3 style="margin: 0 0 5px 0;"><a href="{row['job_url']}" style="color: #2980b9; text-decoration: none;">{row['title']}</a></h3>
        <p style="margin: 0; font-size: 14px;"><strong>Empresa:</strong> {row['company']}</p>
        <p style="margin: 0; font-size: 14px; color: #7f8c8d;"><strong>Ubicación:</strong> {row['location']}</p>
    </div>
    """

html_content += "<p style='font-size: 12px; color: #999;'>El reporte completo en CSV se encuentra adjunto a este correo.</p></body></html>"

# 5. Configurar y enviar el correo usando credenciales de GitHub Secrets
remitente = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
destinatario = os.environ.get('MAIL_DESTINO')

msg = MIMEMultipart()
msg['From'] = remitente
msg['To'] = destinatario
msg['Subject'] = "Nuevas Vacantes: Data & Fullstack"
msg.attach(MIMEText(html_content, 'html'))

# Adjuntar el CSV
with open(archivo_csv, "rb") as f:
    adjunto = MIMEApplication(f.read(), _subtype="csv")
    adjunto.add_header('Content-Disposition', 'attachment', filename=archivo_csv)
    msg.attach(adjunto)

# Conexión al servidor SMTP de Gmail
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(remitente, password)
    server.send_message(msg)
    server.quit()
    print("Correo enviado exitosamente.")
except Exception as e:
    print(f"Error al enviar correo: {e}")
