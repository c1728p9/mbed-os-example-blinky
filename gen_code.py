from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("."),
)

def repeat(val, count):
    return [val.format(num) for num in range(count)]

def render_partial_args(template, bind_count, arg_count):
    
    def template_typenames(bind_count, arg_count):
        builder = ["typename R"]
        builder.extend(repeat("typename A{}", arg_count))
        builder.extend(repeat("typename B{}", bind_count))
        return ", ".join(builder)
    
    def template_specilization(bind_count, arg_count):
        builder = ["R(%s)" % ", ".join(repeat("A{}", arg_count))]
        builder.extend(repeat("B{}", bind_count))
        return ", ".join(builder)
    
    def all_args(bind_count, arg_count):
        builder = []
        builder.extend(repeat("B{}", bind_count))
        builder.extend(repeat("A{}", arg_count))
        return ", ".join(builder)
    assert all_args(5, 5) == "B0, B1, B2, B3, B4, A0, A1, A2, A3, A4"
    
    def ctor_typenames(bind_count, arg_count):
        return ""
#         builder = []
#         builder.extend(repeat("typename C{}", bind_count))
#         if not builder:
#             return ""
#         return "template <%s>" % ", ".join(builder)
#     assert ctor_typenames(0, 0) == ""
#     assert ctor_typenames(5, 5) == "template <typename C0, typename C1, typename C2, typename C3, typename C4>"
    
    def ctor_args(bind_count, arg_count):
        builder = []
        builder.extend(repeat("B{0} b{0}", bind_count))
        return ", ".join(builder)
    assert ctor_args(5, 5) == "B0 b0, B1 b1, B2 b2, B3 b3, B4 b4"
    
    def ctor_values(bind_count, arg_count):
        builder = []
        builder.extend(repeat("b{0}", bind_count))
        return ", ".join(builder)
    assert ctor_values(5, 5) == "b0, b1, b2, b3, b4"
    
    def set_args(bind_count, arg_count):
        builder = []
        builder.extend(repeat("A{0} a{0}", arg_count))
        return ", ".join(builder)
    assert set_args(5, 5) == "A0 a0, A1 a1, A2 a2, A3 a3, A4 a4"
    
    def set_code(bind_count, arg_count):
        return ["all.b%s = a%s;" % (val + bind_count, val) for val in range(arg_count)]
    
    dict = {
        "template_typenames": template_typenames(bind_count, arg_count),
        "template_specilization": template_specilization(bind_count, arg_count),
        "all_args": all_args(bind_count, arg_count),
#         "ctor_typenames": ctor_typenames(bind_count, arg_count),
        "ctor_args": ctor_args(bind_count, arg_count),
        "ctor_values": ctor_values(bind_count, arg_count),
        "set_args": set_args(bind_count, arg_count),
        "set_code" : set_code(bind_count, arg_count),
    }
    print template.render(**dict)

partial_args = env.get_template('PartialArgs.tmpl')
for i in range(6):
    for j in range(6):
        render_partial_args(partial_args, i,j)


def template_typenames(count, mode):
    modes = {
        "callable": "typename F",   # The callable itself
        "pointer": "typename R",    # Function pointer return value
    }
    builder = [modes[mode]]
    builder.extend(repeat("typename B{}", count))
    return ", ".join(builder)
assert template_typenames(10, "callable") == "typename F, typename B0, typename B1, typename B2, typename B3, typename B4, typename B5, typename B6, typename B7, typename B8, typename B9"
assert template_typenames(10, "pointer") == "typename R, typename B0, typename B1, typename B2, typename B3, typename B4, typename B5, typename B6, typename B7, typename B8, typename B9"

def template_specilization(count, mode):
    args = repeat("B{}", count)
    args.extend(repeat("void", 10 - count))
    modes = {
        "callable": "F",
        "pointer": "R(%s)" % ", ".join(repeat("B{}", count)),
    }
    builder = [modes[mode]]
    builder.extend(args)
    return ", ".join(builder)
assert template_specilization(0, "callable") == "F, void, void, void, void, void, void, void, void, void, void"
assert template_specilization(10, "callable") == "F, B0, B1, B2, B3, B4, B5, B6, B7, B8, B9"
assert template_specilization(10, "pointer") == "R(B0, B1, B2, B3, B4, B5, B6, B7, B8, B9), B0, B1, B2, B3, B4, B5, B6, B7, B8, B9"

def template_fields(count, mode):
    modes = {
        "callable": "F f;",
        "pointer": "R(*f)(%s);" % ", ".join(repeat("B{}", count)),
    }
    builder = [modes[mode]]
    builder.extend(repeat("B{0} b{0};", count))
    return " ".join(builder)
assert template_fields(10, "callable") == "F f; B0 b0; B1 b1; B2 b2; B3 b3; B4 b4; B5 b5; B6 b6; B7 b7; B8 b8; B9 b9;"
assert template_fields(10, "pointer") == "R(*f)(B0, B1, B2, B3, B4, B5, B6, B7, B8, B9); B0 b0; B1 b1; B2 b2; B3 b3; B4 b4; B5 b5; B6 b6; B7 b7; B8 b8; B9 b9;"
 
def ctor_args(count, mode):
    modes = {
        "callable": "F f",
        "pointer": "R(*f)(%s)" % ", ".join(repeat("B{}", count)),
    }
    builder = [modes[mode]]
    builder.extend(repeat("B{0} b{0}=B{0}()", count))
    return ", ".join(builder)
assert ctor_args(10, "callable") == "F f, B0 b0=B0(), B1 b1=B1(), B2 b2=B2(), B3 b3=B3(), B4 b4=B4(), B5 b5=B5(), B6 b6=B6(), B7 b7=B7(), B8 b8=B8(), B9 b9=B9()"
assert ctor_args(10, "pointer") == "R(*f)(B0, B1, B2, B3, B4, B5, B6, B7, B8, B9), B0 b0=B0(), B1 b1=B1(), B2 b2=B2(), B3 b3=B3(), B4 b4=B4(), B5 b5=B5(), B6 b6=B6(), B7 b7=B7(), B8 b8=B8(), B9 b9=B9()"

def ctor_values(count, mode):
    builder = ["f(f)"]
    builder.extend(repeat("b{0}(b{0})", count))
    return ", ".join(builder)
assert ctor_values(10, "callable") == "f(f), b0(b0), b1(b1), b2(b2), b3(b3), b4(b4), b5(b5), b6(b6), b7(b7), b8(b8), b9(b9)"
assert ctor_values(10, "pointer") == "f(f), b0(b0), b1(b1), b2(b2), b3(b3), b4(b4), b5(b5), b6(b6), b7(b7), b8(b8), b9(b9)"

def call_and_destroy(count, mode):
    builder = []
    builder.extend(repeat("s->b{0}", count))
    return "s->f(%s)" % ", ".join(builder)
assert call_and_destroy(10, "callable") == "s->f(s->b0, s->b1, s->b2, s->b3, s->b4, s->b5, s->b6, s->b7, s->b8, s->b9)"
assert call_and_destroy(10, "pointer") == "s->f(s->b0, s->b1, s->b2, s->b3, s->b4, s->b5, s->b6, s->b7, s->b8, s->b9)"


def render_all_args(template, count, variant):
    dict = {
        "template_typenames": template_typenames(count, variant),
        "template_specilization": template_specilization(count, variant),
        "template_fields": template_fields(count, variant),
        "ctor_args": ctor_args(count, variant),
        "ctor_values": ctor_values(count, variant),
        "call_and_destroy": call_and_destroy(count, variant),
    }
    print template.render(**dict)

# all_args = env.get_template('AllArgs.tmpl')
# for i in range(11):
#     for mode in ("callable", "pointer"):
#         render_all_args(all_args, i, mode)
