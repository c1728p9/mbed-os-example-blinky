from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("."),
#     autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.tmpl')
template2 = env.get_template('template2.tmpl')

# print(typename_args)
def repeat(val, count):
    return ", ".join(val.format(num) for num in range(count))

def render(bind_count, arg_count):
    dict = {
        "typename_args": repeat("typename A{0}", arg_count),#, ".join("typename A" + str(val) for val in range(arg_count))
        "typename_binds": repeat("typename B{0}", bind_count),#", ".join("typename B" + str(val) for val in range(bind_count))
        "args": repeat("A{0}", arg_count),#, ".join("A" + str(val) for val in range(bind_count))
        "binds": repeat("B{0}", arg_count),
        "ctor_typename_args": repeat("typename C{0}", arg_count),
        "ctor_args": repeat("C{0} c{0}", bind_count),
        "ctor_values": repeat("c{0}", arg_count),
        "set_args": repeat("A{0} a{0}", arg_count),
        "set_code": ["all.b%s = a%s" % (val + bind_count, val) for val in range(arg_count)]
    }
    print template.render(**dict)
# for i in range(5):
#     for j in range(5):
#         render(i,j)

def repeat2(val, count):
    return [val.format(num) for num in range(count)]

def template_typenames(bind_count, arg_count):
    builder = ["typename R"]
    builder.extend(repeat2("typename A{}", arg_count))
    builder.extend(repeat2("typename B{}", bind_count))
    return ", ".join(builder)

def template_specilization(bind_count, arg_count):
    builder = ["R(%s)" % ", ".join(repeat2("A{}", arg_count))]
    builder.extend(repeat2("B{}", bind_count))
    return ", ".join(builder)

def all_args(bind_count, arg_count):
    builder1 = repeat2("B{}", bind_count)
    builder1.extend(repeat2("A{}", arg_count))
    builder = ["void(*)(%s)" % ", ".join(builder1)]
    builder.extend(repeat2("B{}", bind_count))
    builder.extend(repeat2("A{}", arg_count))
    return ", ".join(builder)
assert all_args(5, 5) == "void(*)(B0, B1, B2, B3, B4, A0, A1, A2, A3, A4), B0, B1, B2, B3, B4, A0, A1, A2, A3, A4"

def ctor_typenames(bind_count, arg_count):
    builder = ["typename F"]
    builder.extend(repeat2("typename C{}", bind_count))
    return ", ".join(builder)
assert ctor_typenames(5, 5) == "typename F, typename C0, typename C1, typename C2, typename C3, typename C4"

def ctor_args(bind_count, arg_count):
    builder = ["F f"]
    builder.extend(repeat2("C{0} c{0}", bind_count))
    return ", ".join(builder)
assert ctor_args(5, 5) == "F f, C0 c0, C1 c1, C2 c2, C3 c3, C4 c4"

def ctor_values(bind_count, arg_count):
    builder = ["f"]
    builder.extend(repeat2("c{0}", bind_count))
    return ", ".join(builder)
assert ctor_values(5, 5) == "f, c0, c1, c2, c3, c4"

def set_args(bind_count, arg_count):
    builder = []
    builder.extend(repeat2("A{0} a{0}", arg_count))
    return ", ".join(builder)
assert set_args(5, 5) == "A0 a0, A1 a1, A2 a2, A3 a3, A4 a4"

def set_code(bind_count, arg_count):
    return ["all.b%s = a%s;" % (val + bind_count, val) for val in range(arg_count)]

def render2(bind_count, arg_count):
    dict = {
        "template_typenames": template_typenames(bind_count, arg_count),
        "template_specilization": template_specilization(bind_count, arg_count),
        "all_args": all_args(bind_count, arg_count),
        "ctor_typenames": ctor_typenames(bind_count, arg_count),
        "ctor_args": ctor_args(bind_count, arg_count),
        "ctor_values": ctor_values(bind_count, arg_count),
        "set_args": set_args(bind_count, arg_count),
        "set_code" : set_code(bind_count, arg_count),
    }
    print template2.render(**dict)

for i in range(6):
    for j in range(6):
        render2(i,j)

# template <typename R, typename A0, typename A1, typename A2, typename A3, typename A4, typename B0, typename B1, typename B2, typename B3, typename B4>
# struct PartialArgs<R(A0, A1, A2, A3, A4), B0, B1, B2, B3, B4> {
#     typedef AllArgs<void(*)(B0, B1, B2, B3, B4, A0, A1, A2, A3, A4), B0, B1, B2, B3, B4, A0, A1, A2, A3, A4> AllArgs;
#     AllArgs all;
# 
#     template <typename F, typename C0, typename C1, typename C2, typename C3, typename C4>
#     PartialArgs(F f, C0 c0, C1 c1, C2 c2, C3 c3, C4 c4): all(f, c0, c1, c2, c3, c4) { }
# 
#     void set(A0 a0, A1 a1, A2 a2, A3 a3, A4 a4) {
#         all.b5 = a0;
#         all.b6 = a1;
#         all.b7 = a2;
#         all.b8 = a3;
#         all.b9 = a4;
#     }
# };

# {{typename_args}} typename A0, typename A1, typename A2, typename A3, typename A4,
# {{typename_binds}} typename B0, typename B1, typename B2, typename B3, typename B4
# {{args}} A0, A1, A2, A3, A4
# {{binds}} B0, B1, B2, B3, B4
# {{ctor_typename_args}} typename C0, typename C1, typename C2, typename C3, typename C4
# {{ctor_args}} C0 c0, C1 c1, C2 c2, C3 c3, C4 c4
# {{ctor_values}} c0, c1, c2, c3, c4
# {{set_args}} A0 a0, A1 a1, A2 a2, A3 a3, A4 a4
# {{set_code}}
#         all.b5 = a0;
#         all.b6 = a1;
#         all.b7 = a2;
#         all.b8 = a3;
#         all.b9 = a4;
# 
# A0 a0, A1 a1, A2 a2, A3 a3, A4 a4
# #         all.b5 = a0;
# #         all.b6 = a1;
# #         all.b7 = a2;
# #         all.b8 = a3;
# #         all.b9 = a4;
# 
# 
# C0 c0, C1 c1, C2 c2, C3 c3, C4 c4
# 
# {{typename_args}}
# {{typename_binds}}
# {{args}}
# {{binds}}