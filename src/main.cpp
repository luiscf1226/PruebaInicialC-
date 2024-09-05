#include <iostream>
#include <vector>
#include <string>
#include "estudiante.h"

// Función para calcular el promedio de calificaciones
double calcularPromedio(const std::vector<double>& calificaciones) {
    double suma = 0;
    for (const auto& calificacion : calificaciones) {
        suma += calificacion;
    }
    return calificaciones.empty() ? 0 : suma / calificaciones.size();
}

// Función principal del programa
int main() {
    // Crear un vector de estudiantes
    std::vector<Estudiante> estudiantes;

    // Agregar algunos estudiantes
    estudiantes.push_back(Estudiante("Juan Pérez", 20));
    estudiantes.push_back(Estudiante("María García", 22));
    estudiantes.push_back(Estudiante("Carlos López", 19));

    // Agregar calificaciones a los estudiantes
    estudiantes[0].agregarCalificacion(85.5);
    estudiantes[0].agregarCalificacion(90.0);
    estudiantes[1].agregarCalificacion(78.5);
    estudiantes[1].agregarCalificacion(92.5);
    estudiantes[2].agregarCalificacion(88.0);
    estudiantes[2].agregarCalificacion(76.5);

    // Imprimir información de los estudiantes
    for (const auto& estudiante : estudiantes) {
        std::cout << "Nombre: " << estudiante.obtenerNombre() << std::endl;
        std::cout << "Edad: " << estudiante.obtenerEdad() << std::endl;
        std::cout << "Promedio: " << calcularPromedio(estudiante.obtenerCalificaciones()) << std::endl;
        std::cout << std::endl;
    }

    return 0;
}
