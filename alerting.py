import os
import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class AlertManager:
    def __init__(self, threshold=0.5, log_file='logs/alerts.log',
                 smtp_host=None, smtp_port=587, smtp_user=None,
                 smtp_password=None, email_from=None, email_to=None):
        self.threshold = float(os.environ.get('ANOMALY_THRESHOLD', threshold))
        self.log_file = Path(os.environ.get('ALERT_LOG_FILE', log_file))

        self.smtp_host = smtp_host or os.environ.get('SMTP_HOST')
        self.smtp_port = int(smtp_port or os.environ.get('SMTP_PORT', 587))
        self.smtp_user = smtp_user or os.environ.get('SMTP_USER')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD')
        self.email_from = email_from or os.environ.get('ALERT_EMAIL_FROM')
        self.email_to = email_to or os.environ.get('ALERT_EMAIL_TO')

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(f'anomalyshield.alerts.{id(self)}')
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(handler)

    def process(self, results):
        if isinstance(results, dict):
            results = [results]

        alerts = []
        for r in results:
            score = float(r.get('score', 0))
            prediction = int(r.get('prediction', 0))
            if prediction == 1 and score >= self.threshold:
                alerts.append(r)
                self._log_alert(r)

        if alerts:
            self._send_alert_email(alerts)

        return alerts

    def _log_alert(self, r):
        self.logger.warning('ALERT - anomalie detectee - score=%.4f', r.get('score', 0))

    def _send_alert_email(self, alerts):
        if not (self.smtp_host and self.email_from and self.email_to):
            self.logger.info('%d alerte(s) non envoyee(s) par email (SMTP non configure)', len(alerts))
            return

        lines = [f'- score={a.get("score", 0):.4f}' for a in alerts]
        body = (
            f'AnomalyShield a detecte {len(alerts)} anomalie(s) le '
            f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.\n\n'
            + '\n'.join(lines)
        )

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = f'[AnomalyShield] {len(alerts)} anomalie(s) detectee(s)'
        msg['From'] = self.email_from
        msg['To'] = self.email_to

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                if self.smtp_user:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            self.logger.info('Email d\'alerte envoye a %s', self.email_to)
        except Exception as e:
            self.logger.error('Echec de l\'envoi email: %s', e)
