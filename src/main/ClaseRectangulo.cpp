// ClaseRectangulo.cpp
#include "ClaseRectangulo.h"

// Constructor de la clase Rectángulo
ClaseRectangulo::ClaseRectangulo(double l, double a) : largo(l), ancho(a) {}

// Método para calcular el área del rectángulo
double ClaseRectangulo::calcularArea() {
    return largo * ancho;
}

// Método para calcular el perímetro del rectángulo
double ClaseRectangulo::calcularPerimetro() {
    return 2 * (largo + ancho);
}

