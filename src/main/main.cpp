#include <iostream>
#include <vector>
#include <string>

// Clase para representar un estudiante
class Estudiante {
private:
    std::string nombre;
    int edad;
    std::vector<double> calificaciones;

public:
    Estudiante(std::string n, int e) : nombre(n), edad(e) {}

    void agregarCalificacion(double calificacion) {
        calificaciones.push_back(calificacion);
    }

    double calcularPromedio() {
        if (calificaciones.empty()) return 0.0;
        double suma = 0.0;
        for (double calificacion : calificaciones) {
            suma += calificacion;
        }
        return suma / calificaciones.size();
    }

    void imprimirInformacion() {
        std::cout << "Nombre: " << nombre << ", Edad: " << edad << std::endl;
        std::cout << "Calificaciones: ";
        for (double calificacion : calificaciones) {
            std::cout << calificacion << " ";
        }
        std::cout << std::endl;
        std::cout << "Promedio: " << calcularPromedio() << std::endl;
    }
};

// Función para encontrar el estudiante con el promedio más alto
Estudiante* encontrarMejorEstudiante(std::vector<Estudiante>& estudiantes) {
    if (estudiantes.empty()) return nullptr;
    
    Estudiante* mejorEstudiante = &estudiantes[0];
    double mejorPromedio = estudiantes[0].calcularPromedio();

    for (int i = 1; i < estudiantes.size(); i++) {
        double promedioActual = estudiantes[i].calcularPromedio();
        if (promedioActual > mejorPromedio) {
            mejorPromedio = promedioActual;
            mejorEstudiante = &estudiantes[i];
        }
    }

    return mejorEstudiante;
}

int main() {
    std::vector<Estudiante> listaEstudiantes;

    // Crear algunos estudiantes de ejemplo
    Estudiante estudiante1("Juan", 20);
    estudiante1.agregarCalificacion(8.5);
    estudiante1.agregarCalificacion(9.0);
    estudiante1.agregarCalificacion(7.5);

    Estudiante estudiante2("María", 22);
    estudiante2.agregarCalificacion(9.5);
    estudiante2.agregarCalificacion(9.0);
    estudiante2.agregarCalificacion(9.5);

    Estudiante estudiante3("Carlos", 21);
    estudiante3.agregarCalificacion(7.0);
    estudiante3.agregarCalificacion(8.0);
    estudiante3.agregarCalificacion(8.5);

    listaEstudiantes.push_back(estudiante1);
    listaEstudiantes.push_back(estudiante2);
    listaEstudiantes.push_back(estudiante3);

    // Imprimir información de todos los estudiantes
    for (Estudiante& estudiante : listaEstudiantes) {
        estudiante.imprimirInformacion();
        std::cout << "------------------------" << std::endl;
    }

    // Encontrar y mostrar el estudiante con el mejor promedio
    Estudiante* mejorEstudiante = encontrarMejorEstudiante(listaEstudiantes);
    if (mejorEstudiante != nullptr) {
        std::cout << "El estudiante con el mejor promedio es:" << std::endl;
        mejorEstudiante->imprimirInformacion();
    } else {
        std::cout << "No hay estudiantes en la lista." << std::endl;
    }

    return 0;
}
