"""
Serviço de envio de emails via SMTP.
Se EMAIL_HOST não estiver configurado, imprime o link no terminal (modo desenvolvimento).
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_FROM, BASE_URL

logger = logging.getLogger(__name__)


def _template_recuperacao(link: str, nome: str = "") -> str:
    saudacao = f"Olá{', ' + nome.split()[0] if nome else ''}!"
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #1F0900; padding: 32px 16px;">
        <div style="max-width: 520px; margin: 0 auto;">

            <div style="text-align: center; margin-bottom: 28px;">
                <p style="font-size: 28px; font-weight: 900; color: #ffffff; letter-spacing: 6px; margin: 0;">MEU RU</p>
                <p style="color: #F4792088; font-size: 13px; margin: 4px 0 0;">Restaurante Universitário · UFCAT</p>
            </div>

            <div style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                <div style="height: 4px; background: linear-gradient(90deg, #F47920, #E03D3D);"></div>
                <div style="padding: 36px 32px;">
                    <h2 style="color: #111; font-size: 20px; margin: 0 0 8px;">Recuperação de Senha</h2>
                    <p style="color: #555; font-size: 14px; margin: 0 0 24px;">{saudacao}</p>
                    <p style="color: #555; font-size: 14px; line-height: 1.6; margin: 0 0 32px;">
                        Recebemos uma solicitação para redefinir a senha da sua conta.<br>
                        Clique no botão abaixo para criar uma nova senha:
                    </p>
                    <div style="text-align: center; margin-bottom: 32px;">
                        <a href="{link}"
                           style="background: linear-gradient(135deg, #F47920, #E03D3D); color: #fff;
                                  padding: 14px 32px; border-radius: 10px; text-decoration: none;
                                  font-weight: bold; font-size: 15px; display: inline-block;">
                            Redefinir Senha
                        </a>
                    </div>
                    <p style="color: #999; font-size: 13px; margin: 0 0 16px;">
                        Este link é válido por <strong>1 hora</strong>. Se você não solicitou a redefinição,
                        ignore este e-mail — sua senha permanece a mesma.
                    </p>
                    <p style="color: #bbb; font-size: 12px; margin: 0; word-break: break-all;">
                        Se o botão não funcionar, copie e cole este link no navegador:<br>
                        <a href="{link}" style="color: #F47920;">{link}</a>
                    </p>
                </div>
            </div>

            <p style="text-align: center; color: #F4792044; font-size: 11px; margin-top: 24px;">
                Sistema de Créditos · Restaurante Universitário UFCAT
            </p>
        </div>
    </body>
    </html>
    """


def _template_boas_vindas(nome: str, matricula: str) -> str:
    primeiro_nome = nome.split()[0] if nome else "Aluno"
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #1A1A1A; padding: 32px 16px;">
        <div style="max-width: 520px; margin: 0 auto;">

            <div style="text-align: center; margin-bottom: 28px;">
                <p style="font-size: 28px; font-weight: 900; color: #ffffff; letter-spacing: 6px; margin: 0;">MEU RU</p>
                <p style="color: #F4792088; font-size: 13px; margin: 4px 0 0;">Restaurante Universitário · UFCAT</p>
            </div>

            <div style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                <div style="height: 4px; background: linear-gradient(90deg, #F47920, #E03D3D);"></div>
                <div style="padding: 36px 32px;">
                    <h2 style="color: #111; font-size: 20px; margin: 0 0 16px;">Cadastro realizado com sucesso! 🎉</h2>
                    <p style="color: #555; font-size: 14px; line-height: 1.6; margin: 0 0 20px;">
                        Olá, <strong>{primeiro_nome}</strong>! Sua conta no sistema de créditos do RU foi criada.
                    </p>

                    <div style="background: #FFF7F0; border: 1px solid #F4792033; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px;">
                        <p style="margin: 0 0 6px; font-size: 13px; color: #999; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Seus dados de acesso</p>
                        <p style="margin: 0 0 4px; font-size: 14px; color: #333;"><strong>Matrícula:</strong> {matricula}</p>
                    </div>

                    <p style="color: #555; font-size: 14px; line-height: 1.6; margin: 0 0 28px;">
                        Agora você pode acompanhar seu saldo de créditos, histórico de refeições e muito mais pelo portal.
                    </p>

                    <div style="text-align: center; margin-bottom: 28px;">
                        <a href="{BASE_URL}/login"
                           style="background: linear-gradient(135deg, #F47920, #E03D3D); color: #fff;
                                  padding: 14px 32px; border-radius: 10px; text-decoration: none;
                                  font-weight: bold; font-size: 15px; display: inline-block;">
                            Acessar o Portal
                        </a>
                    </div>

                    <p style="color: #bbb; font-size: 12px; margin: 0; text-align: center;">
                        Se você não realizou este cadastro, entre em contato com a administração do RU.
                    </p>
                </div>
            </div>

            <p style="text-align: center; color: #F4792044; font-size: 11px; margin-top: 24px;">
                Sistema de Créditos · Restaurante Universitário UFCAT
            </p>
        </div>
    </body>
    </html>
    """


def _template_alerta(mensagem: str) -> str:
    linhas = mensagem.replace("\n", "<br>")
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #1A1A1A; padding: 32px 16px;">
        <div style="max-width: 520px; margin: 0 auto;">
            <div style="text-align: center; margin-bottom: 28px;">
                <p style="font-size: 28px; font-weight: 900; color: #ffffff; letter-spacing: 6px; margin: 0;">MEU RU</p>
                <p style="color: #F4792088; font-size: 13px; margin: 4px 0 0;">Restaurante Universitário · UFCAT</p>
            </div>
            <div style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                <div style="height: 4px; background: linear-gradient(90deg, #F47920, #E03D3D);"></div>
                <div style="padding: 36px 32px;">
                    <h2 style="color: #111; font-size: 20px; margin: 0 0 20px;">Aviso do Restaurante Universitário</h2>
                    <p style="color: #333; font-size: 15px; line-height: 1.7; margin: 0 0 28px;">{linhas}</p>
                    <div style="text-align: center;">
                        <a href="{BASE_URL}/login"
                           style="background: linear-gradient(135deg, #F47920, #E03D3D); color: #fff;
                                  padding: 12px 28px; border-radius: 10px; text-decoration: none;
                                  font-weight: bold; font-size: 14px; display: inline-block;">
                            Acessar o Portal
                        </a>
                    </div>
                </div>
            </div>
            <p style="text-align: center; color: #F4792044; font-size: 11px; margin-top: 24px;">
                Sistema de Créditos · Restaurante Universitário UFCAT
            </p>
        </div>
    </body>
    </html>
    """


def enviar_email_alerta(email: str, assunto: str, mensagem: str) -> bool:
    return enviar_emails_alerta_lote([email], assunto, mensagem) == 1


def enviar_emails_alerta_lote(emails: list[str], assunto: str, mensagem: str) -> int:
    """Envia o mesmo alerta para vários destinatários usando uma única conexão SMTP."""
    if not emails:
        return 0
    if not EMAIL_HOST:
        logger.info("[DEV] Email alerta simulado para %d destinatários: %s", len(emails), mensagem)
        return len(emails)
    html = _template_alerta(mensagem)
    enviados = 0
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
            servidor.ehlo()
            servidor.starttls()
            if EMAIL_USER and EMAIL_PASS:
                servidor.login(EMAIL_USER, EMAIL_PASS)
            for email in emails:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = assunto
                    msg["From"] = EMAIL_FROM
                    msg["To"] = email
                    msg.attach(MIMEText(html, "html", "utf-8"))
                    servidor.sendmail(EMAIL_FROM, [email], msg.as_string())
                    enviados += 1
                except Exception as exc:
                    logger.error("Falha ao enviar para %s: %s", email, exc)
    except Exception as exc:
        logger.error("Erro na conexão SMTP ao enviar alertas: %s", exc)
    return enviados


def enviar_email_boas_vindas(email: str, nome: str, matricula: str) -> bool:
    """
    Envia email de confirmação de cadastro ao novo aluno.
    Em modo dev (sem EMAIL_HOST), imprime no terminal.
    """
    if not EMAIL_HOST:
        print("\n" + "="*60)
        print("📧 [MODO DEV] Email de boas-vindas")
        print(f"   Para: {email}  |  Nome: {nome}  |  Matrícula: {matricula}")
        print("="*60 + "\n")
        logger.info("[DEV] Email de boas-vindas simulado para %s", email)
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo ao RU — Cadastro confirmado!"
        msg["From"] = EMAIL_FROM
        msg["To"] = email

        msg.attach(MIMEText(_template_boas_vindas(nome, matricula), "html", "utf-8"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
            servidor.ehlo()
            servidor.starttls()
            if EMAIL_USER and EMAIL_PASS:
                servidor.login(EMAIL_USER, EMAIL_PASS)
            servidor.sendmail(EMAIL_FROM, [email], msg.as_string())

        logger.info("Email de boas-vindas enviado para %s", email)
        return True

    except Exception as exc:
        logger.error("Erro ao enviar email de boas-vindas para %s: %s", email, exc)
        return False


def enviar_email_recuperacao(email: str, token: str, nome: str = "") -> bool:
    """
    Envia email de recuperação de senha.
    Retorna True se enviado com sucesso.
    Em modo dev (sem EMAIL_HOST), imprime o link no terminal.
    """
    link = f"{BASE_URL}/recuperar-senha/{token}"

    # ── Modo desenvolvimento: sem servidor SMTP configurado ──
    if not EMAIL_HOST:
        print("\n" + "="*60)
        print("📧 [MODO DEV] Email de recuperação de senha")
        print(f"   Para: {email}")
        print(f"   Link: {link}")
        print("="*60 + "\n")
        logger.info(f"[DEV] Link de recuperação para {email}: {link}")
        return True

    # ── Modo produção: envio real via SMTP ───────────────────
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Recuperação de Senha — RU"
        msg["From"] = EMAIL_FROM
        msg["To"] = email

        html_content = _template_recuperacao(link, nome)
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
            servidor.ehlo()
            servidor.starttls()
            if EMAIL_USER and EMAIL_PASS:
                servidor.login(EMAIL_USER, EMAIL_PASS)
            servidor.sendmail(EMAIL_FROM, [email], msg.as_string())

        logger.info(f"Email de recuperação enviado para {email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email para {email}: {e}")
        return False
