// ClaseRectangulo.h
#ifndef CLASERECTANGULO_H
#define CLASERECTANGULO_H

class ClaseRectangulo {
private:
    double largo;
    double ancho;
public:
    ClaseRectangulo(double l, double a);
    double calcularArea();
    double calcularPerimetro();
};

#endif // CLASERECTANGULO_H

