#!/bin/bash

# Crear la estructura de directorios
mkdir -p src test scripts .github/workflows input expected_output output

# Crear archivos necesarios (vacíos o con contenido básico)
touch test/test_main.cpp
touch scripts/analyze_structure.py scripts/analyze_libraries.py scripts/analyze_identation.py
touch scripts/analyze_spelling.py scripts/run_moss.py scripts/sonar_qube.py
touch scripts/run_plagiarism.py scripts/generate_report.py
touch .github/workflows/ci.yml
touch README.md

# Crear archivos JSON para entradas, pasos esperados y salidas esperadas
cat << EOF > input/input.json
{
  "steps": [
    {
      "input": "1",
      "description": "Seleccionar opción 1 del menú principal"
    },
    {
      "input": "Juan",
      "description": "Ingresar nombre del usuario"
    },
    {
      "input": "3",
      "description": "Seleccionar opción 3 para salir"
    }
  ]
}
EOF

cat << EOF > expected_output/expected_steps.json
{
  "steps": [
    {
      "output": "Bienvenido al programa. Seleccione una opción:",
      "description": "Mensaje de bienvenida y opciones del menú"
    },
    {
      "output": "Ha seleccionado la opción 1. Por favor, ingrese su nombre:",
      "description": "Confirmación de selección y solicitud de nombre"
    },
    {
      "output": "Hola, Juan. Gracias por usar el programa.",
      "description": "Saludo personalizado"
    },
    {
      "output": "Saliendo del programa. ¡Hasta luego!",
      "description": "Mensaje de despedida"
    }
  ]
}
EOF

cat << EOF > expected_output/expected_final_output.json
{
  "final_output": "Programa ejecutado correctamente. Todas las opciones del menú funcionan como se espera."
}
EOF

# Añadir contenido básico al README
cat << EOF > README.md
# Proyecto C++

Este es el repositorio para tu proyecto C++ en Visual Studio.

## Instrucciones

1. Clona este repositorio.
2. Crea tu proyecto en Visual Studio.
3. Copia todos los archivos de tu proyecto a la carpeta 'src' de este repositorio.
4. Asegúrate de que tu programa principal se llame 'main.cpp' y esté en la carpeta 'src'.
5. Actualiza este README con la información específica de tu proyecto.

## Estructura del Proyecto

- src/: Contiene los archivos fuente de tu proyecto.
- test/: Para tus archivos de prueba.
- scripts/: Scripts de análisis y evaluación.
- input/: Archivos JSON con entradas de prueba.
- expected_output/: Archivos JSON con salidas esperadas.
- output/: Donde se guardarán los reportes de análisis.

## Notas Adicionales

- Asegúrate de no subir archivos binarios o de compilación al repositorio.
- Mantén tu código limpio y bien documentado.
- Sigue las mejores prácticas de programación en C++.
EOF

# Crear un .gitignore básico para C++ y Visual Studio
cat << EOF > .gitignore
# Archivos objeto compilados
*.o
*.obj

# Archivos de librería compilados
*.lib
*.a
*.dll
*.so

# Ejecutables
*.exe
*.out

# Archivos de Visual Studio
.vs/
*.user
*.suo
*.sln
*.vcxproj
*.vcxproj.filters

# Directorios de compilación
[Dd]ebug/
[Rr]elease/
x64/
x86/
[Bb]in/
[Oo]bj/

# Archivos temporales
*.tmp
*.temp

# Otros archivos y carpetas que generalmente no se quieren en el control de versiones
*.log
.vscode/

# Ignorar todos los archivos en la carpeta output excepto .gitkeep
output/*
!output/.gitkeep
EOF

# Crear .gitkeep en la carpeta output
touch output/.gitkeep

# Copiar el script de análisis
cat << EOF > scripts/analyze_project.py
${document_content}
EOF

echo "Estructura del repositorio creada con éxito. El estudiante puede crear su proyecto de Visual Studio y mover los archivos relevantes a la carpeta 'src'."
echo "El script de análisis 'analyze_project.py' ha sido copiado a la carpeta 'scripts' y analizará todos los archivos .cpp en 'src' y sus subdirectorios."
