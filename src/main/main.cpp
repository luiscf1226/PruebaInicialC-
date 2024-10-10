#include <iostream>
#include <vector>
#include <string>

using namespace std;

// Estructura para representar a un estudiante
struct Estudiante {
    string nombre;
    int edad;
    vector<double> calificaciones;
};

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

// Función para mostrar la información de un estudiante
void mostrarEstudiante(const Estudiante& estudiante) {
    cout << "Nombre: " << estudiante.nombre << endl;
    cout << "Edad: " << estudiante.edad << endl;
    cout << "Promedio: " << calcularPromedio(estudiante.calificaciones) << endl;
    cout << "------------------------" << endl;
}

int main() {
    vector<Estudiante> estudiantes = {
        {"Juan", 20, {8.5, 9.0, 7.5}},
        {"Maria", 22, {9.5, 8.0, 9.5}},
        {"Carlos", 21, {7.0, 8.5, 8.0}}
    };
    
    // Mostrar información de los estudiantes
    for (const auto& estudiante : estudiantes) {
        mostrarEstudiante(estudiante);
    }

    return 0;
}
