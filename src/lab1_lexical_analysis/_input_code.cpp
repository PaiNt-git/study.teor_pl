// function_log.cpp
#include <iostream>
#include <cstdlib>
// "Математические функции".
#include <cmath>

// Определение своей функции.
double log(double base, double arg)
{
  // Через стандартный натуральный логарифм.
  return std::log(arg) / std::log(base);
}


int main()
{
  using namespace std;

  double a = 0.1, b = 0; // Числа с плавающей запятой.
  cout << "a = ";
  cin >> a;
  cout << "b = ";
  cin >> b;

  cout.precision(16); // 16 значащих знаков.
  cout << "log(b, a)  = " << log(b, a) << endl;
	return EXIT_SUCCESS;
}
