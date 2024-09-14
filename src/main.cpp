#include <iostream>
#include <string>

int main() {
    int opcion;
    std::string nombre;
    int edad;

    // Paso 1: Mostrar mensaje de bienvenida y opciones del menú
    std::cout << "Bienvenido al programa. Por favor, seleccione una opción:" << std::endl;
    std::cout << "1. Ingresar datos del usuario" << std::endl;
    std::cout << "2. Ver otros datos" << std::endl;
    std::cout << "3. Salir" << std::endl;
    
    std::cin >> opcion;

    // Paso 2: Seleccionar opción 1
    if (opcion == 1) {
        std::cout << "Ha seleccionado la opción 1. Por favor, ingrese su nombre:" << std::endl;
        std::cin >> nombre;
        
        // Paso 3: Solicitar la edad
        std::cout << "Ahora, ingrese su edad:" << std::endl;
        std::cin >> edad;

        // Paso 4: Mostrar la información ingresada
        std::cout << "Hola, " << nombre << ". Tienes " << edad << " años. Gracias por usar el programa." << std::endl;
    }

    // Paso 5: Salir del programa
    std::cout << "Saliendo del programa. ¡Hasta luego!" << std::endl;

    return 0;
}
