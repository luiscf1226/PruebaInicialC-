// ClaseCirculo.cpp
#include "ClaseCirculo.h"
#define PI 3.14159265358979323846

// Constructor de la clase Círculo
ClaseCirculo::ClaseCirculo(double r) : radio(r) {}

// Método para calcular el área del círculo
double ClaseCirculo::calcularArea() {
    return PI * radio * radio;
}

// Método para calcular el perímetro (circunferencia) del círculo
double ClaseCirculo::calcularPerimetro() {
    return 2 * PI * radio;
}

