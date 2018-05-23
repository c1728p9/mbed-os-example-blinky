#include "mbed.h"

template<typename A0, typename A1, typename A2, typename A3>
struct AllArgs;

template<typename A0, typename A1, typename A2, typename A3>
struct AllArgs {
    typedef AllArgs<A0, A1, A2, A3> Self;

    A0 a0; A1 a1; A2 a2; A3 a3;

    template<typename T0, typename T1>
    AllArgs(T0 a0, T1 a1=A1(), A2 a2=A2(), A3 a3=A3()): a0(a0), a1(a1), a2(a2), a3(a3) {}

    template <typename T, typename _>
    struct Operations {
        static void copy(void *_dest, void *_src)
        {
            new (_dest) Self(*(Self*)_src);
        }

        static void call(void *data) {
            Self *s = static_cast<Self*>(data);
            s->a0(s->a1, s->a2, s->a3);
            s->~Self();
        }
    };

    template <typename T, typename R, typename U>
    struct Operations<T*, R (U::*)(A2, A3)> {
        static void copy(void *_dest, void *_src)
        {
            new (_dest) Self(*(Self*)_src);
        }

        static void call(void *data) {
            Self *s = static_cast<Self*>(data);
            ((s->a0)->*(s->a1))(s->a2, s->a3);
            s->~Self();
        }
    };

    template <typename T, typename R, typename U>
    struct Operations<T, R (U::*)(A2, A3) const> {
        static void copy(void *_dest, void *_src)
        {
            new (_dest) Self(*(Self*)_src);
        }

        static void call(void *data) {
            Self *s = static_cast<Self*>(data);
            ((s->a0)->*(s->a1))(s->a2, s->a3);
            s->~Self();
        }
    };

    template <typename T, typename R, typename U>
    struct Operations<T, R (U::*)(A2, A3) volatile> {
        static void copy(void *_dest, void *_src)
        {
            new (_dest) Self(*(Self*)_src);
        }

        static void call(void *data) {
            Self *s = static_cast<Self*>(data);
            ((s->a0)->*(s->a1))(s->a2, s->a3);
            s->~Self();
        }
    };

    template <typename T, typename R, typename U>
    struct Operations<T, R (U::*)(A2, A3) const volatile> {
        static void copy(void *_dest, void *_src)
        {
            new (_dest) Self(*(Self*)_src);
        }

        static void call(void *data) {
            Self *s = static_cast<Self*>(data);
            ((s->a0)->*(s->a1))(s->a2, s->a3);
            s->~Self();
        }
    };

    typedef Operations<A0, A1> ops;
};



class Test {
public:
    void print_test_args(int a, int b) {
        printf("CLASS: A %i B %i\r\n", a, b);
    }

    void print_test_args_c(int a, int b) const {
        printf("CLASS c: A %i B %i\r\n", a, b);
    }

    void print_test_args_v(int a, int b) volatile {
        printf("CLASS v: A %i B %i\r\n", a, b);
    }

    void print_test_args_cv(int a, int b) const volatile {
        printf("CLASS cv: A %i B %i\r\n", a, b);
    }

};

DigitalOut led1(LED1);

void print_args(int a, int b, int c)
{
    printf("A %i B %i C %i\r\n", a, b, c);
}



//template <typename A0>
//void call_function(void *obj, A0 a0)
//{
//    AllArgs<int, int, int>::ops<A0, void>::call(obj);
//}
//
//template <typename A0>
//void copy_function(void *obj, uint32_t size, A0 a0)
//{
//    uint8_t *buf = new uint8_t[sizeof(AllArgs<int, int, int>)];
//    AllArgs<int, int, int>::ops<A0, void>::copy((void*)buf, obj);
//    AllArgs<int, int, int>::ops<A0, void>::call((void*)buf);
//}
//
//
//template <typename A0, typename A1>
//void call_function(void *obj, A0 a0, A1 a1)
//{
//    AllArgs<int, int, int>::ops<A0, A1>::call(obj);
//}
//

template <typename T>
void copy_function(void *obj)
{
    uint8_t *buf = new uint8_t[sizeof(T)];
    T::ops::copy((void*)buf, obj);
    T::ops::call((void*)buf);
    delete[] buf;
}

struct CallableTest {
    void operator()(int a, int b, int c) {
        printf("Callable function %i, %i, %i\r\n", a, b, c);
    }
};


// main() runs in its own thread in the OS
int main() {

//    AllArgs<int, int, int> args(print_args, 8, 9);
//
//
//    call_function((void*)&args, print_args);
//    copy_function((void*)&args,sizeof(args), print_args);
//
//    Test t;
////    t.print_test_args_cv(1,2,3);
//    Callback<void(int, int, int)> cb(&t, &Test::print_test_args_cv);
//
//    AllArgs<int, int, int> args2(&t, &Test::print_test_args, 9);
//    call_function((void*)&args2, &t, &Test::print_test_args);
//    copy_function((void*)&args2,sizeof(args2), &t, &Test::print_test_args);
//
//    volatile Test t_c;
//
//    AllArgs<int, int, int> args3(&t_c, &Test::print_test_args_cv, 9);
//    call_function((void*)&args3, &t_c, &Test::print_test_args_cv);
//    copy_function((void*)&args3,sizeof(args3), &t_c, &Test::print_test_args_cv);
//

    AllArgs<void(*)(int, int, int), int, int, int> args0(print_args, 1, 2, 3);
    AllArgs<void(*)(int, int, int), int, int, int>::ops::call((void*) &args0);


    Test t;
    AllArgs<const Test*, void (Test::*)(int, int) const volatile, int, int> args1(&t, &Test::print_test_args_cv, 2, 3);
    AllArgs<const Test*, void (Test::*)(int, int) const volatile, int, int>::ops::call((void*) &args1);

    CallableTest ct;
    AllArgs<CallableTest, int, int, int> args2(ct, 1, 2, 3);
    AllArgs<CallableTest, int, int, int>::ops::call((void*) &args2);
    copy_function< AllArgs<CallableTest, int, int, int> >((void*)&args2);

    while (true) {
        led1 = !led1;
        wait(0.5);
    }
}

