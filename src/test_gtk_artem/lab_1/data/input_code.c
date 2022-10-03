#include <iostream>
using namespace std;

/*
    ************* Команда компиляции: *************
g++ input_code.c -o input_code && chmod +x input_code && ./input_code
*/

int main()
{
    string name;
    int age;
    const int anniversary = 5;  // частота

    printf("Введите ваш возраст и имя:\n");
    cin >> name >> age;

    if (age % anniversary == 0) {
        cout << name << " поздравляем с юбилеем!\n";
    } else {
        int wait_years = abs(age % anniversary - anniversary);
        cout << name << " придется подождать! До юбилея осталось ";
        for (int i = 1; i <= wait_years; i++) {
            cout << '*';
        }
        cout << " года\n";
    }

    return 0;
}

