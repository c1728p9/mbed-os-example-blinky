#include "mbed.h"


struct __class;
typedef union {
    void (*_staticfunc)();
    void (*_boundfunc)(__class*);
    void (__class::*_methodfunc)();
} function_storage_t;
typedef void* object_storage_t;

template<typename A0, typename A1, typename A2>
struct AllArgs;

template<typename A0, typename A1, typename A2>
struct AllArgs {
    typedef AllArgs<A0, A1, A2> Self;
    function_storage_t function;
    object_storage_t object;

    A0 a0; A1 a1; A2 a2;

    template<typename R>
    AllArgs(R(*f)(A0, A1, A2), A0 a0=A0(), A1 a1=A1(), A2 a2=A2()): a0(a0), a1(a1), a2(a2)
    {
        typedef R(*function_t)(A0, A1, A2);
        *(function_t*)(&this->function) = f;
        object = NULL;
    }

    template<typename T, typename R>
    AllArgs(T *obj, R (T::*method)(A0, A1, A2), A0 a0=A0(), A1 a1=A1(), A2 a2=A2()): a0(a0), a1(a1), a2(a2)
    {
        typedef R (T::*method_t)(A0, A1, A2);
        typedef T * object_t;
        *(method_t*)(&this->function) = method;
        *(object_t*)(&this->object) = obj;
    }

    template<typename T, typename R>
    AllArgs(const T *obj, R (T::*method)(A0, A1, A2) const, A0 a0=A0(), A1 a1=A1(), A2 a2=A2()): a0(a0), a1(a1), a2(a2)
    {
        typedef R (T::*method_t)(A0, A1, A2) const;
        typedef const T * object_t;
        *(method_t*)(&this->function) = method;
        *(object_t*)(&this->object) = obj;
    }

    template<typename T, typename R>
    AllArgs(volatile T *obj, R (T::*method)(A0, A1, A2) volatile, A0 a0=A0(), A1 a1=A1(), A2 a2=A2()): a0(a0), a1(a1), a2(a2)
    {
        typedef R (T::*method_t)(A0, A1, A2) volatile;
        typedef volatile T * object_t;
        *(method_t*)(&this->function) = method;
        *(object_t*)(&this->object) = obj;
    }

    template<typename T, typename R>
    AllArgs(const volatile T *obj, R (T::*method)(A0, A1, A2) const volatile, A0 a0=A0(), A1 a1=A1(), A2 a2=A2()): a0(a0), a1(a1), a2(a2)
    {
        typedef R (T::*method_t)(A0, A1, A2) const volatile;
        typedef const volatile T * object_t;
        *(method_t*)(&this->function) = method;
        *(object_t*)(&this->object) = obj;
    }

    template <typename T0, typename T1=void>
    struct ops;

    template <typename R>
    struct ops<R(*)(A0, A1, A2), void> {
        static void copy(void *_dest, void *_src)
        {
            Self *dest = (Self*)_dest;
            Self *src = (Self*)_src;
            new (dest) Self(*(Self*)src);
            dest->function = src->function;
            dest->object = src->object;
        }

        static void call(void *data) {
            typedef R(*function_t)(A0, A1, A2);
            Self *s = static_cast<Self*>(data);
            (*((function_t*)&s->function))(s->a0, s->a1, s->a2);
            s->~Self();
        }
    };

    template <typename T, typename R>
    struct ops<T*, R (T::*)(A0, A1, A2)> {
        static void copy(void *_dest, void *_src)
        {
            Self *dest = (Self*)_dest;
            Self *src = (Self*)_src;
            new (dest) Self(*(Self*)src);
            dest->function = src->function;
            dest->object = src->object;
        }

        static void call(void *data) {
            typedef R (T::*method_t)(A0, A1, A2);
            typedef T * object_t;
            Self *s = static_cast<Self*>(data);
            object_t object = (object_t)s->object;
            method_t method = *((method_t*)&s->function);
            (object->*method)(s->a0, s->a1, s->a2);
            s->~Self();
        }
    };

    template <typename R, typename T, typename U>
    struct ops<U*, R (T::*)(A0, A1, A2) const> {
        static void copy(void *_dest, void *_src)
        {
            Self *dest = (Self*)_dest;
            Self *src = (Self*)_src;
            new (dest) Self(*(Self*)src);
            dest->function = src->function;
            dest->object = src->object;
        }

        static void call(void *data) {
            typedef R (T::*method_t)(A0, A1, A2) const;
            typedef const T * object_t;
            Self *s = static_cast<Self*>(data);
            object_t object = (object_t)s->object;
            method_t method = *((method_t*)&s->function);
            (object->*method)(s->a0, s->a1, s->a2);
            s->~Self();
        }
    };

    template <typename R, typename T, typename U>
    struct ops<U*, R (T::*)(A0, A1, A2) volatile> {
        static void copy(void *_dest, void *_src)
        {
            Self *dest = (Self*)_dest;
            Self *src = (Self*)_src;
            new (dest) Self(*(Self*)src);
            dest->function = src->function;
            dest->object = src->object;
        }

        static void call(void *data) {
            typedef R (T::*method_t)(A0, A1, A2) volatile;
            typedef volatile T * object_t;
            Self *s = static_cast<Self*>(data);
            object_t object = (object_t)s->object;
            method_t method = *((method_t*)&s->function);
            (object->*method)(s->a0, s->a1, s->a2);
            s->~Self();
        }
    };

    template <typename R, typename T, typename U>
    struct ops<U*, R (T::*)(A0, A1, A2) const volatile> {
        static void copy(void *_dest, void *_src)
        {
            Self *dest = (Self*)_dest;
            Self *src = (Self*)_src;
            new (dest) Self(*(Self*)src);
            dest->function = src->function;
            dest->object = src->object;
        }

        static void call(void *data) {
            typedef R (T::*method_t)(A0, A1, A2) const volatile;
            typedef const volatile T * object_t;
            Self *s = static_cast<Self*>(data);
            object_t object = (object_t)s->object;
            method_t method = *((method_t*)&s->function);
            (object->*method)(s->a0, s->a1, s->a2);
            s->~Self();
        }
    };

};



class Test {
public:
    void print_test_args(int a, int b, int c) {
        printf("CLASS: A %i B %i C %i\r\n", a, b, c);
    }

    void print_test_args_c(int a, int b, int c) const {
        printf("CLASS c: A %i B %i C %i\r\n", a, b, c);
    }

    void print_test_args_v(int a, int b, int c) volatile {
        printf("CLASS v: A %i B %i C %i\r\n", a, b, c);
    }

    void print_test_args_cv(int a, int b, int c) const volatile {
        printf("CLASS cv: A %i B %i C %i\r\n", a, b, c);
    }

};

DigitalOut led1(LED1);

void print_args(int a, int b, int c)
{
    printf("A %i B %i C %i\r\n", a, b, c);
}



template <typename A0>
void call_function(void *obj, A0 a0)
{
    AllArgs<int, int, int>::ops<A0, void>::call(obj);
}

template <typename A0>
void copy_function(void *obj, uint32_t size, A0 a0)
{
    uint8_t *buf = new uint8_t[sizeof(AllArgs<int, int, int>)];
    AllArgs<int, int, int>::ops<A0, void>::copy((void*)buf, obj);
    AllArgs<int, int, int>::ops<A0, void>::call((void*)buf);
}


template <typename A0, typename A1>
void call_function(void *obj, A0 a0, A1 a1)
{
    AllArgs<int, int, int>::ops<A0, A1>::call(obj);
}

template <typename A0, typename A1>
void copy_function(void *obj, uint32_t size, A0 a0, A1 a1)
{
    uint8_t *buf = new uint8_t[sizeof(AllArgs<int, int, int>)];
    AllArgs<int, int, int>::ops<A0, A1>::copy((void*)buf, obj);
    AllArgs<int, int, int>::ops<A0, A1>::call((void*)buf);
}

// main() runs in its own thread in the OS
int main() {
    AllArgs<int, int, int> args(print_args, 8, 9);


    call_function((void*)&args, print_args);
    copy_function((void*)&args,sizeof(args), print_args);

    Test t;
//    t.print_test_args_cv(1,2,3);
    Callback<void(int, int, int)> cb(&t, &Test::print_test_args_cv);

    AllArgs<int, int, int> args2(&t, &Test::print_test_args, 9);
    call_function((void*)&args2, &t, &Test::print_test_args);
    copy_function((void*)&args2,sizeof(args2), &t, &Test::print_test_args);

    volatile Test t_c;

    AllArgs<int, int, int> args3(&t_c, &Test::print_test_args_cv, 9);
    call_function((void*)&args3, &t_c, &Test::print_test_args_cv);
    copy_function((void*)&args3,sizeof(args3), &t_c, &Test::print_test_args_cv);


    while (true) {
        led1 = !led1;
        wait(0.5);
    }
}

