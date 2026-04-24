import re
import os

# =========================
# CONFIG
# =========================
arquivo_entrada = "dados.sql"
pasta_saida = "pdfs"
os.makedirs(pasta_saida, exist_ok=True)

# =========================
# LEITURA
# =========================
with open(arquivo_entrada, "r", encoding="utf-8", errors="ignore") as f:
    conteudo = f.read()

# pega todos os blobs hex
blobs = re.findall(r"X'([0-9A-Fa-f]+)'", conteudo)

print(f"Total de blobs encontrados: {len(blobs)}")

salvos = 0
ignorados = 0

# =========================
# PROCESSAMENTO
# =========================
for i, hex_data in enumerate(blobs):
    try:
        # só PDFs (%PDF)
        if not hex_data.startswith("25504446"):
            ignorados += 1
            continue

        pdf_bytes = bytes.fromhex(hex_data)

        # pega parte inicial (rápido)
        header = pdf_bytes[:20000].decode("latin1", errors="ignore")

        # sinais de texto
        tem_texto = any(x in header for x in [
            "BT", "/Font", "Tf", "Tj", "TJ"
        ])

        # sinais fortes de imagem
        eh_imagem_forte = all(x in header for x in [
            "/Subtype", "/Image", "DCTDecode"
        ])

        # decisão
        if tem_texto:
            caminho = os.path.join(pasta_saida, f"{salvos}.pdf")

            with open(caminho, "wb") as f:
                f.write(pdf_bytes)

            print(f"Salvo: {caminho}")
            salvos += 1
        else:
            ignorados += 1

    except Exception as e:
        print(f"Erro no blob {i}: {e}")
        ignorados += 1

# =========================
# RESULTADO
# =========================
print("\n===== RESULTADO =====")
print(f"PDFs salvos (texto): {salvos}")
print(f"Ignorados (imagem/outros): {ignorados}")