#include <iostream>
#include <vector>
#include <string>

class Person {
 public:
  Person(const std::string& n, int a) : name(n), age(a) {}

  std::string getName() const { return name; }
  int getAge() const { return age; }

 private:
  std::string name;
  int age;
};

class Group {
 public:
  void addMember(const Person& person) {
    members.push_back(person);
  }

  void printMembers() const {
    for (const auto& member : members) {
      std::cout << member.getName() << " (" << member.getAge() << " years old)" << std::endl;
    }
  }

 private:
  std::vector<Person> members;
};

int main() {
  Group myGroup;

  myGroup.addMember(Person("Alice", 25));
  myGroup.addMember(Person("Bob", 30));
  myGroup.addMember(Person("Charlie", 35));

  std::cout << "Group members:" << std::endl;
  myGroup.printMembers();

  int x = 10;
  int y = 20;

  if (x < y) {
    std::cout << "x is less than y" << std::endl;
  } else {
    std::cout << "x is greater than or equal to y" << std::endl;
  }

  for (int i = 0; i < 5; ++i) {
    std::cout << "Iteration " << i + 1 << std::endl;
  }

  return 0;
}
