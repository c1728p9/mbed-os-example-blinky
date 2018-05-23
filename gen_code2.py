from string import Formatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("."),
)


class CaseFormatter(Formatter):
    def convert_field(self, value, conversion):
        if conversion == 'u':
            return value.upper()
        elif conversion == 'l':
            return value.lower()
        else:
            return Formatter.convert_field(self, value, conversion)

fmt = CaseFormatter()
#print(fmt.format("test {0} {0!u} {0!l}", "HeLlo"))
#print(fmt.format("test {0} {0!u} {0!l}", "A0"))

def repeat(val, count):
    return [val.format(num) for num in range(count)]

def format(format, values):
    return [fmt.format(format, value) for value in values]

def format_and_join(values, format, join_str):
    return join_str.join(fmt.format(format, value) for value in values)
#join(Ts, "{!u}", " ,")

def pad_list(values, pad, count):
    pad_count = count - len(values)
    assert pad_count >= 0
    result = []
    result.extend(values)
    result.extend([pad] * pad_count)
    return result

args_max = 12
arg_combinations = [["B%i" % arg_num for arg_num in range(arg_count)] for arg_count in range(1, args_max)]


class Namespace:
    pass

function_pointer = Namespace()
function_pointer.ctor_template_params = ["R"]
function_pointer.ctor_template_specilizations = "R(*)({0})" #TODO -args
function_pointer.ctor_args = ["R(*)({0}) f"]
function_pointer.create = "*(R(*)())({0}->function) = f"                            # 0 = 'this' pointer
function_pointer.copy = "*(R(*)())({0}->function) = *(R(*)())({1}->function)"       # 0 = dest 'this' 1 = source 'this'
function_pointer.call = "((F*)&s->storage)"
#function_pointer.destroy = "((F*)&s->storage)->~F()"


functions = [
    function_pointer
]


all_args = env.get_template('AllArgs2.tmpl')
dict = {
    "arg_combinations": arg_combinations,
    "join": format_and_join,
    "functions": functions,
    "args_max": args_max,
    "pad_list": pad_list,
    "format": format
#    "template_typenames": template_typenames(count, variant),
#    "template_specilization": template_specilization(count, variant),
#    "template_fields": template_fields(count, variant),
#    "ctor_args": ctor_args(count, variant),
#    "ctor_values": ctor_values(count, variant),
#    "call_and_destroy": call_and_destroy(count, variant),
}
print all_args.render(**dict)


# for i in range(6):
#     for j in range(6):
#         render_partial_args(partial_args, i,j)


#def template_typenames(count, mode):
#    modes = {
#        "callable": "typename F",   # The callable itself
#        "pointer": "typename R",    # Function pointer return value
#    }
#    builder = [modes[mode]]
#    builder.extend(repeat("typename B{}", count))
#    return ", ".join(builder)
#assert template_typenames(10, "callable") == "typename F, typename B0, typename B1, typename B2, typename B3, typename B4, typename B5, typename B6, typename B7, typename B8, typename B9"
#assert template_typenames(10, "pointer") == "typename R, typename B0, typename B1, typename B2, typename B3, typename B4, typename B5, typename B6, typename B7, typename B8, typename B9"
#
#def template_specilization(count, mode):
#    args = repeat("B{}", count)
#    args.extend(repeat("void", 10 - count))
#    modes = {
#        "callable": "F",
#        "pointer": "R(*)(%s)" % ", ".join(repeat("B{}", count)),
#    }
#    builder = [modes[mode]]
#    builder.extend(args)
#    return ", ".join(builder)
#assert template_specilization(0, "callable") == "F, void, void, void, void, void, void, void, void, void, void"
#assert template_specilization(10, "callable") == "F, B0, B1, B2, B3, B4, B5, B6, B7, B8, B9"
#assert template_specilization(10, "pointer") == "R(*)(B0, B1, B2, B3, B4, B5, B6, B7, B8, B9), B0, B1, B2, B3, B4, B5, B6, B7, B8, B9"
#
#def template_fields(count, mode):
#    modes = {
#        "callable": "F f;",
#        "pointer": "R(*f)();",
#    }
#    builder = [modes[mode]]
#    builder.extend(repeat("B{0} b{0};", count))
#    return " ".join(builder)
#assert template_fields(10, "callable") == "F f; B0 b0; B1 b1; B2 b2; B3 b3; B4 b4; B5 b5; B6 b6; B7 b7; B8 b8; B9 b9;"
#assert template_fields(10, "pointer") == "R(*f)(); B0 b0; B1 b1; B2 b2; B3 b3; B4 b4; B5 b5; B6 b6; B7 b7; B8 b8; B9 b9;"
#
#def ctor_args(count, mode):
#    modes = {
#        "callable": "F f",
#        "pointer": "R(*f)()",
#    }
#    builder = [modes[mode]]
#    builder.extend(repeat("B{0} b{0}=B{0}()", count))
#    return ", ".join(builder)
#assert ctor_args(10, "callable") == "F f, B0 b0=B0(), B1 b1=B1(), B2 b2=B2(), B3 b3=B3(), B4 b4=B4(), B5 b5=B5(), B6 b6=B6(), B7 b7=B7(), B8 b8=B8(), B9 b9=B9()"
#assert ctor_args(10, "pointer") == "R(*f)(), B0 b0=B0(), B1 b1=B1(), B2 b2=B2(), B3 b3=B3(), B4 b4=B4(), B5 b5=B5(), B6 b6=B6(), B7 b7=B7(), B8 b8=B8(), B9 b9=B9()"
#
#def ctor_values(count, mode):
#    builder = ["f(f)"]
#    builder.extend(repeat("b{0}(b{0})", count))
#    return ", ".join(builder)
#assert ctor_values(10, "callable") == "f(f), b0(b0), b1(b1), b2(b2), b3(b3), b4(b4), b5(b5), b6(b6), b7(b7), b8(b8), b9(b9)"
#assert ctor_values(10, "pointer") == "f(f), b0(b0), b1(b1), b2(b2), b3(b3), b4(b4), b5(b5), b6(b6), b7(b7), b8(b8), b9(b9)"
#
#def call_and_destroy(count, mode):
#    builder = []
#    builder.extend(repeat("s->b{0}", count))
#    return "s->f(%s)" % ", ".join(builder)
#assert call_and_destroy(10, "callable") == "s->f(s->b0, s->b1, s->b2, s->b3, s->b4, s->b5, s->b6, s->b7, s->b8, s->b9)"
#assert call_and_destroy(10, "pointer") == "s->f(s->b0, s->b1, s->b2, s->b3, s->b4, s->b5, s->b6, s->b7, s->b8, s->b9)"
#
#
#def render_all_args(template, count, variant):
#    dict = {
#        "template_typenames": template_typenames(count, variant),
#        "template_specilization": template_specilization(count, variant),
#        "template_fields": template_fields(count, variant),
#        "ctor_args": ctor_args(count, variant),
#        "ctor_values": ctor_values(count, variant),
#        "call_and_destroy": call_and_destroy(count, variant),
#    }
#    print template.render(**dict)
#
#all_args = env.get_template('AllArgs.tmpl')
#for i in range(11):
#    for mode in ("callable", "pointer"):
#        render_all_args(all_args, i, mode)
