#ifndef ESTUDIANTE_H
#define ESTUDIANTE_H

#include <string>
#include <vector>

class Estudiante {
private:
    std::string nombre;
    int edad;
    std::vector<double> calificaciones;

public:
    // Constructor
    Estudiante(const std::string& nombre, int edad) : nombre(nombre), edad(edad) {}

    // Métodos para acceder a los atributos
    std::string obtenerNombre() const { return nombre; }
    int obtenerEdad() const { return edad; }
    const std::vector<double>& obtenerCalificaciones() const { return calificaciones; }

    // Método para agregar una calificación
    void agregarCalificacion(double calificacion) {
        calificaciones.push_back(calificacion);
    }
};

#endif // ESTUDIANTE_H
