#include <iostream>
#include <vector>
#include <string>
#include "estudiante.h"

using namespace std;

// Función para calcular el promedio de calificaciones
double calcularPromedio(const vector<double>& calificaciones) {
    if (calificaciones.empty()) {
        return 0.0;
    }
    double suma = 0.0;
    for (const auto& calificacion : calificaciones) {
        suma += calificacion;
    }
    return suma / calificaciones.size();
}

int main() {
    vector<Estudiante> estudiantes;
    
    // Crear algunos estudiantes de ejemplo
    estudiantes.push_back(Estudiante("Juan", 20, {8.5, 9.0, 7.5}));
    estudiantes.push_back(Estudiante("Maria", 22, {9.5, 8.0, 9.5}));
    estudiantes.push_back(Estudiante("Carlos", 21, {7.0, 8.5, 8.0}));

    // Mostrar información de los estudiantes
    for (const auto& estudiante : estudiantes) {
        cout << "Nombre: " << estudiante.getNombre() << endl;
        cout << "Edad: " << estudiante.getEdad() << endl;
        cout << "Promedio: " << calcularPromedio(estudiante.getCalificaciones()) << endl;
        cout << "------------------------" << endl;
    }
//
    return 0;
}
