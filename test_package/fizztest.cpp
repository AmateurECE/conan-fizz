#include <iostream>
#include <fizz/crypto/RandomGenerator.h>

int main() {
  fizz::RandomGenerator<64> generator;
  std::cout << "The random generated data: ";
  for (const auto& data: generator.generateRandom())
    std::cout << data;
  std::cout << "\n";
}
