"""
Execute este script UMA VEZ para autenticar o Google Sheets.
Uma janela do navegador vai abrir pedindo login com calahdev@gmail.com.
Após autorizar, o token.json será salvo e o app Streamlit poderá ser iniciado.

Uso:
    .venv\Scripts\python autenticar_google.py
"""
import gspread

print("Abrindo navegador para autenticação Google...")
print("Faça login com calahdev@gmail.com e autorize o acesso.\n")

gc = gspread.oauth(
    credentials_filename="credentials.json",
    authorized_user_filename="token.json",
)

print("✓ Autenticação concluída! token.json salvo.")
print("Agora rode: .venv\\Scripts\\streamlit run main.py")
