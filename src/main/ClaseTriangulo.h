// ClaseTriangulo.h
#ifndef CLASETRIANGULO_H
#define CLASETRIANGULO_H

class ClaseTriangulo {
private:
    double base;
    double altura;
public:
    ClaseTriangulo(double b, double h);
    double calcularArea();
    double calcularPerimetro(); // Asumimos un triángulo equilátero para el perímetro
};

#endif // CLASETRIANGULO_H

