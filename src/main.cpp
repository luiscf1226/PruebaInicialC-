#include <iostream>
#include <string>

int main() {
    std::string nombre;
    int edad;
    int opcion;

    std::cout << "Bienvenido al programa. Por favor, seleccione una opción:" << std::endl;
    std::cout << "1. Ingresar información" << std::endl;
    std::cout << "2. Ver información" << std::endl;
    std::cout << "3. Salir" << std::endl;

    std::cin >> opcion;

    switch(opcion) {
        case 1:
            std::cout << "Ha seleccionado la opción 1. Por favor, ingrese su nombre:" << std::endl;
            std::cin >> nombre;
            
            std::cout << "Ahora, ingrese su edad:" << std::endl;
            std::cin >> edad;
            
            std::cout << "Hola, " << nombre << ". Tienes " << edad << " años. Gracias por usar el programa." << std::endl;
            break;
        case 2:
            std::cout << "No hay información para mostrar." << std::endl;
            break;
        case 3:
            std::cout << "Saliendo del programa. ¡Hasta luego!" << std::endl;
            break;
        default:
            std::cout << "Opción no válida." << std::endl;
    }

    return 0;
}
