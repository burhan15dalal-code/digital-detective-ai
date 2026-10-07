#include <iostream>
#include <string>
using namespace std;

class InvestigationObject {
protected:
    int id;
    string name;
public:
    InvestigationObject() : id(0), name("") {}
    InvestigationObject(int i, string n) : id(i), name(n) {}
    int getId() { return id; }
    string getName() { return name; }
    virtual void display() = 0;
    virtual ~InvestigationObject() {}
};

class Suspect : public InvestigationObject {
private:
    int age;
    string location;
    string suspicionLevel;
public:
    Suspect(int i, string n, int a, string l, string s)
        : InvestigationObject(i,n), age(a), location(l), suspicionLevel(s) {}
    void display() override {
        cout << "SUSPECT: " << name << " | Age: " << age
             << " | Location: " << location
             << " | Suspicion: " << suspicionLevel << endl;
    }
};

class Evidence : public InvestigationObject {
private:
    string type, foundAt, description;
public:
    Evidence(int i, string n, string t, string f, string d)
        : InvestigationObject(i,n), type(t), foundAt(f), description(d) {}
    void display() override {
        cout << "EVIDENCE: " << name << " | Type: " << type
             << " | Found at: " << foundAt << endl;
    }
};

class Clue : public InvestigationObject {
private:
    string description, importance;
public:
    Clue(int i, string n, string d, string imp)
        : InvestigationObject(i,n), description(d), importance(imp) {}
    void display() override {
        cout << "CLUE: " << name << " | Importance: " << importance << endl;
    }
};

class InvestigationStack {
private:
    InvestigationObject* stack[100];
    int top;
public:
    InvestigationStack() { top = -1; }

    void push(InvestigationObject* obj) {
        if (top == 99) { cout << "Stack full\n"; return; }
        stack[++top] = obj;
    }

    void pop() {
        if (top == -1) { cout << "Stack empty\n"; return; }
        stack[top]->display();
        delete stack[top--];
    }

    void peek() {
        if (top == -1) { cout << "Stack empty\n"; return; }
        stack[top]->display();
    }

    void search(string name) {
        for (int i = top; i >= 0; i--) {
            if (stack[i]->getName() == name) {
                stack[i]->display();
                return;
            }
        }
        cout << "Record not found\n";
    }

    void deleteByIndex(int index) {
        if (index < 0 || index > top) return;
        delete stack[index];
        for (int i = index; i < top; i++) stack[i] = stack[i+1];
        top--;
    }

    ~InvestigationStack() {
        while (top >= 0) delete stack[top--];
    }
};

int main() {
    InvestigationStack investigation;
    cout << "Digital Detective C++ core ready.\n";
    return 0;
}
