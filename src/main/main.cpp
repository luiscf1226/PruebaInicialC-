#include <iostream>
using namespace std;

int main() {
    // Correctamente acentuadas
    cout << "Hola, ¿cómo estás?" << endl;
    cout << "El niño está en la escuela." << endl;
    
    // Deberían tener acento pero no lo tienen
    cout << "La musica clasica es relajante." << endl;
    cout << "El pajaro volo sobre el arbol." << endl;
    
    // No necesitan acento
    cout << "El perro corre en el parque." << endl;
    cout << "La casa es grande y bonita." << endl;
    
    // Mezcla de correctas e incorrectas
    cout << "José fue al café, pero pidio te." << endl;
    
    // Palabras con tilde en diferentes posiciones
    cout << "Análisis, cántico, matemático" << endl;
    cout << "Telefono, examenes, jovenes" << endl;
    
    // Mayúsculas con y sin acento
    cout << "MÉXICO es un país hermoso." << endl;
    cout << "PERU tiene una rica historia." << endl;
    
    // Frases largas con múltiples casos
    cout << "La educacion es la llave del exito, pero requiere dedicación y esfuerzo." << endl;
    
    return 0;
}
