#ifndef ESTUDIANTE_H
#define ESTUDIANTE_H

#include <string>
#include <vector>

using namespace std;

class Estudiante {
private:
    string nombre;
    int edad;
    vector<double> calificaciones;

public:
    Estudiante(const string& nombre, int edad, const vector<double>& calificaciones);

    string getNombre() const;
    int getEdad() const;
    vector<double> getCalificaciones() const;

    void agregarCalificacion(double calificacion);
    double calcularPromedio() const;
    bool estaAprobado() const;
};

#endif // ESTUDIANTE_H
