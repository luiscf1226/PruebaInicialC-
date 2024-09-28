#include "estudiante.h"

// Constructor de la clase Estudiante
Estudiante::Estudiante(const string& nombre, int edad, const vector<double>& calificaciones)
    : nombre(nombre), edad(edad), calificaciones(calificaciones) {}

// Métodos getter
string Estudiante::getNombre() const {
    return nombre;
}

int Estudiante::getEdad() const {
    return edad;
}

vector<double> Estudiante::getCalificaciones() const {
    return calificaciones;
}

// Método para agregar una nueva calificación
void Estudiante::agregarCalificacion(double calificacion) {
    calificaciones.push_back(calificacion);
}

// Método para calcular el promedio de calificaciones
double Estudiante::calcularPromedio() const {
    if (calificaciones.empty()) {
        return 0.0;
    }
    double suma = 0.0;
    for (const auto& calificacion : calificaciones) {
        suma += calificacion;
    }
    return suma / calificaciones.size();
}

// Método para verificar si el estudiante está aprobado
bool Estudiante::estaAprobado() const {
    return calcularPromedio() >= 6.0;
}
