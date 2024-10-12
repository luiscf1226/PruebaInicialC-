// main.cpp
#include <iostream>
#include "ClaseRectangulo.h"
#include "ClaseCirculo.h"
#include "ClaseTriangulo.h"

int main() {
    // Crear un rectángulo de largo 5 y ancho 3
    ClaseRectangulo rectangulo(5.0, 3.0);
    std::cout << "Área del rectángulo: " << rectangulo.calcularArea() << std::endl;
    std::cout << "Perímetro del rectángulo: " << rectangulo.calcularPerimetro() << std::endl;

    // Crear un círculo de radio 4
    ClaseCirculo circulo(4.0);
    std::cout << "Área del círculo: " << circulo.calcularArea() << std::endl;
    std::cout << "Perímetro del círculo: " << circulo.calcularPerimetro() << std::endl;

    // Crear un triángulo de base 6 y altura 4.
    ClaseTriangulo triangulo(6.0, 4.0);
    std::cout << "Área del triángulo: " << triangulo.calcularArea() << std::endl;
    std::cout << "Perímetro del triángulo: " << triangulo.calcularPerimetro() << std::endl;

    return 0;
}

