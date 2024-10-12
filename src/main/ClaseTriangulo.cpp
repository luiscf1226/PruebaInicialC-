// ClaseTriangulo.cpp
#include "ClaseTriangulo.h"
#include <cmath>

// Constructor de la clase Triángulo
ClaseTriangulo::ClaseTriangulo(double b, double h) : base(b), altura(h) {}

// Método para calcular el área del triángulo
double ClaseTriangulo::calcularArea() {
    return (base * altura) / 2;
}

// Método para calcular el perímetro del triángulo (asumiendo equilátero)
double ClaseTriangulo::calcularPerimetro() {
    return 3 * base;
}

