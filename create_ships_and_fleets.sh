#!/bin/bash

# Script para crear plantillas de barcos y flotas
# Uso: ./create_ships_and_fleets.sh

API_URL="http://localhost:8000/api"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🚀 Iniciando creación de barcos y flotas..."
echo ""

# 1. Login como admin
echo "📝 Autenticando como admin..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_USER}\",\"password\":\"${ADMIN_PASS}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token de autenticación"
    echo "Respuesta: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Autenticación exitosa"
echo ""

# Array para almacenar IDs de barcos creados
declare -a SHIP_IDS

# 2. Crear 15 tipos de barcos
echo "🚢 Creando 15 tipos de barcos..."
echo ""

# Barcos pequeños (2 casillas)
echo "Creando Lancha Patrullera..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lancha Patrullera",
    "size": 2,
    "description": "Embarcación pequeña y rápida"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Lancha Patrullera creada"

echo "Creando Bote Torpedero..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bote Torpedero",
    "size": 2,
    "description": "Pequeño pero letal"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Bote Torpedero creado"

# Barcos medianos (3 casillas)
echo "Creando Submarino..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Submarino",
    "size": 3,
    "description": "Ataca desde las profundidades"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Submarino creado"

echo "Creando Corbeta..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Corbeta",
    "size": 3,
    "description": "Buque de guerra ligero"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Corbeta creada"

echo "Creando Fragata..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fragata",
    "size": 3,
    "description": "Versátil y bien armada"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Fragata creada"

# Barcos grandes (4 casillas)
echo "Creando Destructor..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Destructor",
    "size": 4,
    "description": "Rápido y poderoso"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Destructor creado"

echo "Creando Crucero Ligero..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Crucero Ligero",
    "size": 4,
    "description": "Balance entre velocidad y poder"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Crucero Ligero creado"

echo "Creando Crucero Pesado..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Crucero Pesado",
    "size": 4,
    "description": "Fuertemente blindado"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Crucero Pesado creado"

# Barcos muy grandes (5 casillas)
echo "Creando Acorazado..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acorazado",
    "size": 5,
    "description": "Fortaleza flotante"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Acorazado creado"

echo "Creando Portaaviones..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Portaaviones",
    "size": 5,
    "description": "El barco más grande y poderoso"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Portaaviones creado"

# Barcos especiales
echo "Creando Buque de Asalto Anfibio..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buque de Asalto Anfibio",
    "size": 4,
    "description": "Transporte de tropas y vehículos"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Buque de Asalto Anfibio creado"

echo "Creando Portahelicópteros..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Portahelicópteros",
    "size": 4,
    "description": "Plataforma de helicópteros"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Portahelicópteros creado"

echo "Creando Buque Escolta..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buque Escolta",
    "size": 3,
    "description": "Protección de convoyes"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Buque Escolta creado"

echo "Creando Dragaminas..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dragaminas",
    "size": 2,
    "description": "Especialista en desactivar minas"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Dragaminas creado"

echo "Creando Buque Misiles..."
RESPONSE=$(curl -s -X POST "${API_URL}/admin/ship-templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buque Misiles",
    "size": 3,
    "description": "Armado con misiles de largo alcance"
  }')
SHIP_IDS+=("$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)")
echo "✅ Buque Misiles creado"

echo ""
echo "✅ 15 tipos de barcos creados exitosamente"
echo ""

# 3. Crear 5 flotas con diferentes combinaciones
echo "⚓ Creando 5 flotas..."
echo ""

# Flota 1: Clásica (tablero 10x10)
echo "Creando Flota Clásica..."
FLEET1_SHIPS="[\"${SHIP_IDS[9]}\",\"${SHIP_IDS[8]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[2]}\",\"${SHIP_IDS[0]}\"]"
curl -s -X POST "${API_URL}/admin/base-fleets" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Flota Clásica\",
    \"board_size\": 10,
    \"ship_template_ids\": ${FLEET1_SHIPS}
  }" > /dev/null
echo "✅ Flota Clásica (10x10): Portaaviones, Acorazado, Destructor, Submarino, Lancha"

# Flota 2: Rápida con barcos repetidos (tablero 8x8)
echo "Creando Flota Rápida..."
# 2x Destructor, 1x Crucero Ligero, 2x Submarino, 3x Lancha Patrullera
FLEET2_SHIPS="[\"${SHIP_IDS[5]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[6]}\",\"${SHIP_IDS[2]}\",\"${SHIP_IDS[2]}\",\"${SHIP_IDS[0]}\",\"${SHIP_IDS[0]}\",\"${SHIP_IDS[0]}\"]"
curl -s -X POST "${API_URL}/admin/base-fleets" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Flota Rápida\",
    \"board_size\": 10,
    \"ship_template_ids\": ${FLEET2_SHIPS}
  }" > /dev/null
echo "✅ Flota Rápida (10x10): 2x Destructor, 1x Crucero, 2x Submarino, 3x Lancha"

# Flota 3: Armada Completa (tablero 15x15)
echo "Creando Armada Completa..."
FLEET3_SHIPS="[\"${SHIP_IDS[9]}\",\"${SHIP_IDS[8]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[6]}\",\"${SHIP_IDS[7]}\",\"${SHIP_IDS[2]}\",\"${SHIP_IDS[3]}\",\"${SHIP_IDS[4]}\"]"
curl -s -X POST "${API_URL}/admin/base-fleets" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Armada Completa\",
    \"board_size\": 15,
    \"ship_template_ids\": ${FLEET3_SHIPS}
  }" > /dev/null
echo "✅ Armada Completa (15x15): 8 barcos variados"

# Flota 4: Fuerza de Ataque con barcos repetidos (tablero 12x12)
echo "Creando Fuerza de Ataque..."
# 1x Portaaviones, 3x Destructor, 2x Asalto Anfibio, 2x Buque Misiles
FLEET4_SHIPS="[\"${SHIP_IDS[9]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[5]}\",\"${SHIP_IDS[10]}\",\"${SHIP_IDS[10]}\",\"${SHIP_IDS[14]}\",\"${SHIP_IDS[14]}\"]"
curl -s -X POST "${API_URL}/admin/base-fleets" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Fuerza de Ataque\",
    \"board_size\": 12,
    \"ship_template_ids\": ${FLEET4_SHIPS}
  }" > /dev/null
echo "✅ Fuerza de Ataque (12x12): 1x Portaaviones, 3x Destructor, 2x Asalto, 2x Misiles"

# Flota 5: Defensa Costera con barcos repetidos (tablero 10x10)
echo "Creando Defensa Costera..."
# 2x Corbeta, 2x Fragata, 2x Escolta, 3x Dragaminas
FLEET5_SHIPS="[\"${SHIP_IDS[3]}\",\"${SHIP_IDS[3]}\",\"${SHIP_IDS[4]}\",\"${SHIP_IDS[4]}\",\"${SHIP_IDS[12]}\",\"${SHIP_IDS[12]}\",\"${SHIP_IDS[13]}\",\"${SHIP_IDS[13]}\",\"${SHIP_IDS[13]}\"]"
curl -s -X POST "${API_URL}/admin/base-fleets" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Defensa Costera\",
    \"board_size\": 12,
    \"ship_template_ids\": ${FLEET5_SHIPS}
  }" > /dev/null
echo "✅ Defensa Costera (12x12): 2x Corbeta, 2x Fragata, 2x Escolta, 3x Dragaminas"

echo ""
echo "✅ 5 flotas creadas exitosamente"
echo ""
echo "🎉 ¡Proceso completado!"
echo ""
echo "📊 Resumen:"
echo "   - 15 tipos de barcos creados"
echo "   - 5 flotas configuradas"
echo ""
echo "🎮 Ahora puedes jugar con las siguientes flotas:"
echo "   1. Flota Clásica (10x10) - 5 barcos únicos"
echo "   2. Flota Rápida (10x10) - 8 barcos (con repetidos)"
echo "   3. Armada Completa (15x15) - 8 barcos variados"
echo "   4. Fuerza de Ataque (12x12) - 8 barcos (con repetidos)"
echo "   5. Defensa Costera (12x12) - 9 barcos (con repetidos)"
echo ""
echo "💡 Las flotas 2, 4 y 5 incluyen barcos repetidos del mismo tipo"
echo ""
