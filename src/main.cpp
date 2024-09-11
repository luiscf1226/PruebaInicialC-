#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <map>
#include <cmath>
#include <fstream>

using namespace std;

// Funcion para calcular el promedio
double calcularPromedio(const vector<int>& numeros) {
double suma = 0;
for (int num : numeros) {
suma += num;
}
return suma / numeros.size();
}

int main() {
  cout << "Bienvenido al programa de prueba para los scripts de analisis!" << endl;
  
    vector<int> datos = {10, 20, 30, 40, 50};
    
        // Calculo del promedio
        double promedio = calcularPromedio(datos);
    
  cout << "El promedio de los datos es: " << promedio << endl;
  
      // Prueba de ortografia en español
  cout << "Esto es una prueba de ortografía con algunos errores intencionales." << endl;
  cout << "El perro ladra mucho por la noche." << endl;
  cout << "El gato duerme en el sofa todo el dia." << endl;
  cout << "La computadora es una herramienta muy util." << endl;
  
  // Prueba de identacion incorrecta
    for (int i = 0; i < 5; i++) {
  cout << "Numero: " << i << endl;
      if (i % 2 == 0) {
    cout << "Es par" << endl;
  } else {
          cout << "Es impar" << endl;
      }
    }
  
  // Uso de diferentes tipos de datos y estructuras
  map<string, int> edades;
  edades["Juan"] = 25;
  edades["Maria"] = 30;
  
  // Operaciones matematicas
  double raiz = sqrt(16);
  int potencia = pow(2, 3);
  
  // Manejo de archivos
  ofstream archivo("prueba.txt");
  if (archivo.is_open()) {
    archivo << "Esto es una prueba de escritura en archivo." << endl;
    archivo.close();
  }
  
  cout << "Fin del programa de prueba. Gracias por utilizarlo!" << endl;
  
  return 0;
}
