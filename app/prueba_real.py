import os
from supabase import create_client
from dotenv import load_dotenv

# 1. Cargar variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print("--- DIAGNÓSTICO DE CONEXIÓN ---")

# 2. Verificar credenciales
if not url or not key:
    print("❌ ERROR: No se encontraron URL o KEY en el archivo .env")
    print("Asegúrate de que el archivo se llame exactamente '.env' y tenga tus datos.")
    exit()
else:
    print(f"✅ Credenciales encontradas.")
    print(f"   URL: {url[:20]}...") 

# 3. Intentar conectar
try:
    print("⏳ Conectando a Supabase...")
    supabase = create_client(url, key)
    
    # 4. Leer tabla tickets
    response = supabase.table("tickets").select("*").execute()
    datos = response.data
    
    print(f"✅ Conexión EXITOSA.")
    print(f"📊 Cantidad de tickets encontrados: {len(datos)}")
    
    if len(datos) > 0:
        print("📝 Primer ticket de muestra:")
        print(datos[0])
        print("\nCONCLUSIÓN: Tu base de datos funciona. El problema es visual en Streamlit.")
    else:
        print("\n⚠️ CONCLUSIÓN: La conexión funciona pero LA TABLA ESTÁ VACÍA.")
        print("Debes enviar un correo a tu sistema o insertar un dato manual en Supabase para ver algo.")

except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")
    if "42703" in str(e):
        print("💡 PISTA: Tienes un error de columnas (posiblemente falta created_at o fecha_creacion).")

print("-------------------------------")